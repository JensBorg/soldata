#!/usr/bin/env python3

import binascii
import serial
import serial.rs485
import time 
import datetime
import os 
from gpiozero import LED
import libscrc # CRC16 check
from pathlib import Path
import json
from json import JSONEncoder

Tx_Enable = LED(18)

# python3 read_serial_panel.py
#:ReadQuery1 $END;
#R 43 5A $END;
#E $Addr1(BYTE[2]) $Addr2(BYTE[2]) $Control(BYTE[1]) $Function(BYTE[1]) $Size(BYTE[1]) $END;
#:ReadQuery2 $END;
#E $Data(BYTE[1]) $CheckSum16(BYTE[2]) $END;

# 9600, 8 bit, 1 stop bit (checksum passer med MODBUS checksum)
#2020-05-22 22:53:17.435546: b'01'b'04'b'00'b'0a'b'00'b'10'b'd1'b'c4'.
values1 = (b'\x01\x04\x00\x0a\x00\x10\xd1\xc4')

values11 = bytearray ([0x01, 0x04, 0x00, 0x1e, 0x00, 0x0a, 0x10, 0x0b])

#2020-05-22 22:53:13.385091: b'02'b'04'b'00'b'0a'b'00'b'10'b'd1'b'f7'.
values2 = (b'\x02\x04\x00\x0a\x00\x10\xd1\xf7')
values21 = bytearray ([0x02, 0x04, 0x00, 0x1e, 0x00, 0x0a, 0x10, 0x38])

# subclass JSONEncoder
class DateTimeEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()


def get_filename():
    soldir="/data/soldata/"
    solext=".txt"
    #home = str(Path.home())
    home="/home/pi"
    now = datetime.datetime.now()
    filedate=now.strftime("%Y-%m-%d")
    return home+soldir+filedate+solext

def get_jsonfilename():
    soldir="/data/soldata/"
    solext=".json"
    home="/home/pi"
    now = datetime.datetime.now()
    filedate=now.strftime("%Y-%m-%d")
    return home+soldir+filedate+solext

def GetDataFromInverter(txt,len_return):
#    StartTime=datetime.datetime.now()
#    local_msg=bytearray()
    count=0
    while 1:
        Tx_Enable.on()
#        time.sleep(0.06)
        ser.write(txt)
        ser.flush()
        Tx_Enable.off()
#        time.sleep(0.01)
        
        local_msg=(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        local_msg=ser.read(80)
#        print('Checksum: ',libscrc.modbus(local_msg,0xFFFF),' - ',end='')
#        print(local_msg)
#        print(len(local_msg))
        """
        Here we should check for valid checksum
        Modbus function expect an array of bytes and not a bytearry
        My function needs to be adjusted to use array of bytes before the check can be implemented
        """
        
        if libscrc.modbus(local_msg,0xFFFF)==0: # Validate checksum
            return local_msg
        count=count+1
        if count>5:
            return (b'\x00')
        ser.close()
        time.sleep(0.1)
        ser.open()
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        time.sleep(0.08)
#    EndTime=datetime.datetime.now()
#    TimeUsed=EndTime-StartTime
#    print("Time Used ", TimeUsed.microseconds/1000, " ms")
    return (b'\x00')

def to_value(local_msg,startbyte,length,base):
    local_value=0
    for i in range(length):
        local_value=local_value*256+local_msg[startbyte+i]
    return local_value/base
    
bufsize = 1
msg=bytearray()
#serial.close()
with serial.rs485.RS485('/dev/ttyAMA0', 9600, bytesize=8, parity='N', stopbits=1, timeout=0.1) as ser:
    #ser.rs485_mode = serial.rs485.RS485Settings(True, False)
    #Tx_Enable.off() 
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    time.sleep(0.1)
    while 1:
        got_data=False
        inv = {}
        inv['date'] = datetime.datetime.now()
        inv['inverters'] = []

        filename=get_filename()
        f = open(filename, "a+", buffering=bufsize)
        for y in (1,2):
            InvData = {}
            InvData['Inverter'] = y
            if y==1:
                msg=GetDataFromInverter(values1,39)
            else:
                msg=GetDataFromInverter(values2,39)
            i=len(msg)
            if i>34:
                got_data=True
                txt="Inverter " + format(y) + ", "
                print("Inverter",y," ",end='')
                print("Length msg: ",len(msg)," ",end='')
                txt=txt + "Date " + format(datetime.datetime.now()) + ", "
                print(datetime.datetime.now(), " ",end='')
#                print("0+1: ", msg[0], " - ", msg[1], " - ", (msg[0]*256+msg[1])/10, "")
#                print("2+3: ", msg[2], " - ", msg[3], " - ", (msg[2]*256+msg[3])/10, "")
                InvData['PV Volt'] = to_value(msg,3,2,10)
                txt=txt + "PV Volt " + format(to_value(msg,3,2,10)) + ", "
                print("PV Volt",to_value(msg,3,2,10)," ",end='')
#                print("5+6: ", msg[5], " - ", msg[6], " - ", msg[5]*256+msg[6])
#                print("7+8: ", msg[7], " - ", msg[8], " - ", msg[7]*256+msg[8])
#                print("9+10: ", msg[9], " - ", msg[10], " - ", msg[9]*256+msg[10])
                txt=txt + "Volt " + format(to_value(msg,11,2,10)) + ", "
                print("Volt",to_value(msg,11,2,10)," ",end='')
                InvData['AC Volt'] = to_value(msg,11,2,10)
                
#                print("13+14: ", msg[13], " - ", msg[14], " - ", msg[13]*256+msg[14])
#                print("15+16: ", msg[15], " - ", msg[16], " - ", msg[15]*256+msg[16])
#                print("17+18: ", msg[17], " - ", msg[18], " - ", msg[17]*256+msg[18])
#                print("19+20: ", msg[19], " - ", msg[20], " - ", msg[19]*256+msg[20])
#                print("21+22: ", msg[21], " - ", msg[22], " - ", msg[21]*256+msg[22])
                txt=txt + "Hz " + format(to_value(msg,23,2,100)) + ", "
                print("Hz",to_value(msg,23,2,100)," ",end='')
                InvData['Frequency'] = to_value(msg,23,2,100)
                
#                print("25+26: ", msg[25], " - ", msg[26], " - ", msg[25]*256+msg[26])
                txt=txt + "Watt " + format(to_value(msg,27,2,10)) + ", "
                print("Watt",to_value(msg,27,2,10)," ",end='')
                InvData['AC Power'] = to_value(msg,27,2,10)
                
                txt=txt + "KWatt today " + format(to_value(msg,29,2,10)) + ", "
                print("KWatt today",to_value(msg,29,2,10)," ",end='')
                InvData['Energy Today'] = to_value(msg,29,2,10)
                
                txt=txt + "KWatt total " + format(to_value(msg,31,4,10))
                print("Kwatt total",to_value(msg,31,4,10))
                InvData['Energy total'] = to_value(msg,31,4,10)
                
                txt=txt + "\n"
                f.write(txt)
                inv['inverters'].append(InvData)

            time.sleep(0.2)
        f.close()
        if (got_data):
            filename=get_jsonfilename()
            f = open(filename, "a+", buffering=bufsize,newline='\n')
            f.write(json.dumps(inv, cls=DateTimeEncoder))
            f.write("\n")
            f.close()
        time.sleep(10)
        
