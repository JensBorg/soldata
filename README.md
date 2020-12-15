# SolData is reading data from a KLNE Inverter 3000 and send a JSON structure to a NATS server

The program is now running as a service and writes data to a file every 10 seconds
The current format of the file is commaseparated including some text to explain the value

ToDo
* ~~Change the file format to JSON~~ - done
* Publish the data to a NATS service
* Decided to send data via MQTT instead of NATS
* MQTT is already used in HA for Zigbee communication
* Performance optimization. Currently the file is open and closed for each roundtrip. 
  This should be changed to keep the file open until the date changes.
  When we pass midnight, the current file must be closed and a new file created.
  
Code example:
import paho.mqtt.client as mqtt #import the client1
import paho.mqtt.publish as publish
import time
import random
import json

while True:
    publish.single('home-assistant/solar', payload=json.dumps({"power":random.randrange(0,1000,1),"energy":random.randrange(0,50,1)}), 
        hostname=broker_address, auth={'username':username, 'password':password})
    time.sleep(delay)
