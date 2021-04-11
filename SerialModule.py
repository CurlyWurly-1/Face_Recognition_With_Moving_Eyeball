#import RPi.GPIO as GPIO

# You can check which usb port is used by executing  "ls /dev" 
# To install serial, execute "pip3 install pyserial"
# You also need   to execute "sudo chmod 666 /dev/ttyUSB0"
# You also need   to execute "sudo adduser pete dialout"

import serial     # To install this, use "pip3 install pyserial"
import time

def initConnection(portNo, baudRate):
    try:
        print("Trying to connnect Serial USB")
        ser = serial.Serial(portNo, baudRate)
        ser.flush()
        time.sleep(3)
        print("Device Connected")
        return ser
    except:
        print("Not Connected")


def senddata(serial_device, data, digits):
    myString = "#"
    for d in data:
        myString += str(d).zfill(digits)
    try:
        serial_device.write(myString.encode())
        print(myString)
    except:
        print("Data transmission failed")

if __name__ == "__main__":
    
    ser1 = initConnection('/dev/ttyUSB0', 9600)

    while(True):
        senddata(ser1 , [79, 83], 3)
        time.sleep(1)
        senddata(ser1 , [40, 120], 3)
        time.sleep(1)
