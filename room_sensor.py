 # ZigBee Router Low Address 40C82BEC
 # PANID
 # Zibbee Co-Ordinator Address 40C822DD


import serial
import time
import struct
import json
import requests
from Queue import Queue
from xbee import ZigBee
from collections import namedtuple

PORT = '/dev/ttyAMA0'
BAUD_RATE = 9600
serial_port = serial.Serial(PORT, BAUD_RATE)
message = Queue()

def message_recieved(data):
    message.put(data, block=False)

def post_influx(data):
    payload = "pulse,utility=electric value={0}\n".format(data['electric'])
    payload += "pulse,utility=gas value={0}\n".format(data['gas'])
    print payload
    try:
        r=requests.post("http://192.168.0.14:8086/write?db=mydb", data=payload)
    except requests.exceptions.RequestException, e:
        r = e
    return r


zb = ZigBee(serial_port, callback=message_recieved)

# zb.send('at', command='SH')
# print zb.wait_read_frame()['parameter'].encode('hex')
# zb.send('at', command='SL')
# print zb.wait_read_frame()['parameter'].encode('hex')
def process_message(data):
    rf_data = struct.unpack('<BBB',data['rf_data'])
    if rf_data[0] == 1:
        data = {'gas' : rf_data[1], 'electric': rf_data[2]}
    status = post_influx(data)
    print status.text

while True:
    try:
        time.sleep(.2)
        if message.qsize() > 0:
            msg = message.get_nowait()
            process_message(msg)
    except KeyboardInterrupt:
        break
zb.halt()
serial_port.close()
