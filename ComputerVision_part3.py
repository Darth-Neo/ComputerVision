#! /usr/bin/env python

# Note: Set PLM to sync mode first followed by device sync
# Commands list: http://www.madreporite.com/insteon/commands.htm

import serial, time

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

    # X10 test
    message = bytearray()
    message.append(2)
    message.append(99)
    message.append(176 + 0)
    message.append(0)
    ser.write(message)
    ser.flush()
    time.sleep(0.5)
    message = bytearray()
    message.append(2)
    message.append(99)
    message.append(176 + 2)  # 2 = on, 3 = off
    message.append(128)
    ser.write(message)
    ser.flush()

    ser.close()
