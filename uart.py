#!/usr/bin/env python3
import os
import sys
import pty
import serial


def main() -> int:
    master, slave = pty.openpty()
    m_name = os.ttyname(master)
    print(os.ttyname(slave), m_name)
    ser = serial.Serial(m_name)
    should_stop = False
    while not should_stop:
        raw_msg = ser.readline()
        print('Raw message:', raw_msg)
        msg = raw_msg.decode('utf-8')
        print('Message:', msg)
        if msg == 'quit':
            should_stop = True
    ser.close()
    os.close(slave)
    os.close(master)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('Aborted!')
        sys.exit(1)
