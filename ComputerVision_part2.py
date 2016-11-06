#!/usr/bin/env python

# Note: Set PLM to sync mode first followed by device sync
# Commands list: http://www.madreporite.com/insteon/commands.htm

import serial, binascii

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)


if __name__ == u"__main__":
    ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=19200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0
    )

    ser.flushInput()
    ser.flushOutput()

    reply = ''
    while True:
        string = ser.readline().strip()
        if string != '':
            reply += str(binascii.hexlify(string))
            if len(reply) == 22:
                print(binascii.hexlify(string))
                break

    ser.close()
