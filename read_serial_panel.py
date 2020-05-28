#!/usr/bin/env python3

import binascii
import serial
import serial.rs485
import time 
import datetime
import os 
from gpiozero import LED
import libscrc # CRC16 check

Tx_Enable = LED(18)

# python3 read_serial_panel.py
#:ReadQuery1 $END;
#R 43 5A $END;
#E $Addr1(BYTE[2]) $Addr2(BYTE[2]) $Control(BYTE[1]) $Function(BYTE[1]) $Size(BYTE[1]) $END;
#:ReadQuery2 $END;
#E $Data(BYTE[1]) $CheckSum16(BYTE[2]) $END;


#Inverter 1: b'7f' b'df' b'eb' b'ff' b'df' b'5d' b'77' b'00' b'' b''
#Inverter 2: b'bf' b'df' b'eb' b'ff' b'df' b'5d' b'11' b'00' b'' b''

# 9600, 8 bit, 1 stop bit (checksum passer med MODBUS checksum)
#2020-05-22 22:53:17.435546: b'01'b'04'b'00'b'0a'b'00'b'10'b'd1'b'c4'.
#values1 = bytearray ([0x01, 0x04, 0x00, 0x0a, 0x00, 0x10, 0xd1, 0xc4])
values1 = (b'\x01\x04\x00\x0a\x00\x10\xd1\xc4')


values11 = bytearray ([0x01, 0x04, 0x00, 0x1e, 0x00, 0x0a, 0x10, 0x0b])

#2020-05-22 22:53:13.385091: b'02'b'04'b'00'b'0a'b'00'b'10'b'd1'b'f7'.
#values2 = bytearray ([0x02, 0x04, 0x00, 0x0a, 0x00, 0x10, 0xd1, 0xf7])
values2 = (b'\x02\x04\x00\x0a\x00\x10\xd1\xf7')
values21 = bytearray ([0x02, 0x04, 0x00, 0x1e, 0x00, 0x0a, 0x10, 0x38])


#2020-05-19 20:21:35.958817: b'01'b'04'b'00'b'1e'b'00'b'0a'b'10'b'0b'.
#2020-05-19 18:59:02.968307: b'02'b'04'b'14'b'01'b'51'b'02'b'00'b'00'b'00'b'00'b'00'b'00'b'2b'b'00'b'00'b'00'b'00'b'00'b'00'b'00'b'00'b'00'b'00'b'3f'b'19'
#send b'01'b'04'b'00'b'1e'b'00'b'0a'b'10'b'0b'
#b'01'b'04'b'14'b'01'b'38'b'02'b'00'b'00'b'00'b'00'b'00'b'00'b'29'b'00'b'00'b'00'b'00'b'00'b'00'b'00'b'00'b'00'b'00'b'21'b'd1'b'01'b'04'b'00'b'0a'b'00'b'10'b'd1'b'c4'
#b'01'b'04'b'20'b'0a'b'3a'b'00'b'00'b'00'b'04'b'00'b'00'b'09'b'27'b'00'b'00'b'00'b'00'b'00'b'04'b'00'b'00'b'00'b'00'b'13'b'86'b'00'b'00'b'04'b'34'b'00'b'78'b'00'b'03'b'21'b'64'b'83'b'15'
#send b'02'b'04'b'00'b'0a'b'00'b'10'b'd1'b'f7'.


def write_txt(txt,len_return):
#    StartTime=datetime.datetime.now()
#    local_msg=bytearray()
    count=0
    while 1:
        Tx_Enable.on()
#        time.sleep(0.06)
        ser.write(txt)
        ser.flush()
        Tx_Enable.off()
#        time.sleep(0.08)
        
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
            return b''
        ser.close()
        time.sleep(0.1)
        ser.open()
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        time.sleep(0.08)
#    EndTime=datetime.datetime.now()
#    TimeUsed=EndTime-StartTime
#    print("Time Used ", TimeUsed.microseconds/1000, " ms")
    return b''

def to_value(local_msg,startbyte,length,base):
    local_value=0
    for i in range(length):
        local_value=local_value*256+local_msg[startbyte+i]
    return local_value/base
    
bufsize = 1
f = open("soldata.txt", "a", buffering=bufsize)
msg=bytearray()
#serial.close()
with serial.rs485.RS485('/dev/ttyAMA0', 9600, bytesize=8, parity='N', stopbits=1, timeout=0.1) as ser:
    #ser.rs485_mode = serial.rs485.RS485Settings(True, False)
    #Tx_Enable.off() 
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    time.sleep(0.1)
    while 1:
        for y in (1,2):
            if y==1:
                msg=write_txt(values1,39)
            else:
                msg=write_txt(values2,39)
            i=len(msg)
            if i>34:
                txt="Inverter " + format(y) + ", "
                print("Inverter",y," ",end='')
                txt=txt + "Date " + format(datetime.datetime.now()) + ", "
                print(datetime.datetime.now(), " ",end='')
#                print("0+1: ", msg[0], " - ", msg[1], " - ", (msg[0]*256+msg[1])/10, "")
#                print("2+3: ", msg[2], " - ", msg[3], " - ", (msg[2]*256+msg[3])/10, "")
#                print("3+4: ", msg[3], " - ", msg[4], " - ", (msg[3]*256+msg[4])/10, "PV Volt")
                txt=txt + "PV Volt " + format(to_value(msg,3,2,10)) + ", "
                print("PV Volt",to_value(msg,3,2,10)," ",end='')
#                print("5+6: ", msg[5], " - ", msg[6], " - ", msg[5]*256+msg[6])
#                print("7+8: ", msg[7], " - ", msg[8], " - ", msg[7]*256+msg[8])
#                print("9+10: ", msg[9], " - ", msg[10], " - ", msg[9]*256+msg[10])
#                print("11+12: ", msg[11], " - ", msg[12], " - ", (msg[11]*256+msg[12])/10, "Volt")
                txt=txt + "Volt " + format(to_value(msg,11,2,10)) + ", "
                print("Volt",to_value(msg,11,2,10)," ",end='')
#                print("13+14: ", msg[13], " - ", msg[14], " - ", msg[13]*256+msg[14])
#                print("15+16: ", msg[15], " - ", msg[16], " - ", msg[15]*256+msg[16])
#                print("17+18: ", msg[17], " - ", msg[18], " - ", msg[17]*256+msg[18])
#                print("19+20: ", msg[19], " - ", msg[20], " - ", msg[19]*256+msg[20])
#                print("21+22: ", msg[21], " - ", msg[22], " - ", msg[21]*256+msg[22])
#                print("23+24: ", msg[23], " - ", msg[24], " - ", (msg[23]*256+msg[24])/100, " Hz")
                txt=txt + "Hz " + format(to_value(msg,23,2,100)) + ", "
                print("Hz",to_value(msg,23,2,100)," ",end='')
#                print("25+26: ", msg[25], " - ", msg[26], " - ", msg[25]*256+msg[26])
#                print("27+28: ", msg[27], " - ", msg[28], " - ", (msg[27]*256+msg[28])/10, " Watt")
                txt=txt + "Watt " + format(to_value(msg,27,2,10)) + ", "
                print("Watt",to_value(msg,27,2,10)," ",end='')
#                print("29+30: ", msg[29], " - ", msg[30], " - ", (msg[29]*256+msg[30])/10, " kWatt today")
                txt=txt + "KWatt today " + format(to_value(msg,29,2,10)) + ", "
                print("KWatt today",to_value(msg,29,2,10)," ",end='')
#                print("31+32+33+43: ", msg[31], " - ", msg[32], " - " , msg[33], " - ", msg[34], " - ", (msg[31]*256*65536+msg[32]*65536+ msg[33]*256+msg[34])/10, " kWatt total ")
                txt=txt + "KWatt total " + format(to_value(msg,31,4,10))
                print("Kwatt total",to_value(msg,31,4,10))
                txt=txt + "\n"
                f.write(txt)
            time.sleep(0.2)
        time.sleep(10)
  