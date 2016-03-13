# ZigBee Router Low Address 40C82BEC
 # PANID
 # Zibbee Co-Ordinator Address 40C822DD


import serial
import time
import struct
import json
import requests
import logging
from Queue import Queue
from xbee import ZigBee

message = Queue()

def message_recieved(data):
    message.put(data, block=False)

def post_influx(data):
    payload = "pulse,utility=electric value={0}\n".format(data['electric'])
    payload += "pulse,utility=gas value={0}\n".format(data['gas'])
    try:
        r=requests.post("http://192.168.0.14:8086/write?db=mydb",timeout=(3.05, 6), data=payload)
        if r.status_code == 204:
            logging.info('http-status: %s: payload: %s', r.status_code, payload.replace('\n',','))
    except requests.exceptions.RequestException, e:
        logging.error('%s', e)



# zb.send('at', command='SH')
# print zb.wait_read_frame()['parameter'].encode('hex')
# zb.send('at', command='SL')
# print zb.wait_read_frame()['parameter'].encode('hex')
def process_message(data):
    rf_data = struct.unpack('<BBB',data['rf_data'])
    if rf_data[0] == 1:
        data = {'gas' : rf_data[1], 'electric': rf_data[2]}
    post_influx(data)

def main():
    PORT = '/dev/ttyAMA0'
    BAUD_RATE = 9600

    logging.basicConfig(filename='xListen.log',
        level=logging.DEBUG,
        format='%(asctime)s %(message)s')
    try:
        serial_port = serial.Serial(PORT, BAUD_RATE)
    except serial.SerialException, e:
        logging.error('%s', e)

    zb = ZigBee(serial_port, callback=message_recieved)
    logging.info('Starting to Listen for Xbees')
    while True:
        try:
            time.sleep(.2)
            if message.qsize() > 0:
                logging.debug('message queue: %s ', message.qsize())
                msg = message.get_nowait()
                process_message(msg)
        except KeyboardInterrupt:
            break
    zb.halt()
    serial_port.close()

if __name__ == '__main__':
    main()
