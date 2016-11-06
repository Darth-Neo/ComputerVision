#!/usr/bin/env python
#
# Note: Set PLM to sync mode first followed by device sync
# Commands list: http://www.madreporite.com/insteon/commands.htm

import serial

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

    message = bytearray()
    message.append(0x02)  # INSTEON_PLM_START
    message.append(0x62)  # INSTEON_STANDARD_MESSAGE

    # device id
    message.append(0x29)  # Addr 1
    message.append(0x2A)  # Addr 2
    message.append(0x9F)  # Addr 3

    message.append(0x0F)  # INSTEON_MESSAGE_FLAG
    message.append(0x12)  # 0x12 = FAST ON, 0x14 = FAST OFF, 0x19 = STATUS
    message.append(0xFF)  # 0x00 = 0%, 0xFF = 100%
    ser.write(message)
    ser.flush()

    ser.close()
