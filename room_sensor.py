 # ZigBee Router Low Address 40C82BEC
 # PANID
 # Zibbee Co-Ordinator Address 40C822DD


import serial
import time
import json
from Queue import Queue
from xbee import ZigBee

PORT = '/dev/tty.usbserial-DA01ABFT'
BAUD_RATE = 9600
serial_port = serial.Serial(PORT, BAUD_RATE)
message = Queue()

def message_recieved(data):
    message.put(data, block=False)
    print "W00t"



zb = ZigBee(serial_port, callback=message_recieved)

# zb.send('at', command='SH')
# print zb.wait_read_frame()['parameter'].encode('hex')
# zb.send('at', command='SL')
# print zb.wait_read_frame()['parameter'].encode('hex')
def process_message(data):
    rf = json.loads(data['rf_data'].split('\x00')[0])
    print rf

while True:
    try:
        time.sleep(.1)
        if message.qsize() > 0:
            msg = message.get_nowait()
            process_message(msg)
    except KeyboardInterrupt:
        break
zb.halt()
serial_port.close()
