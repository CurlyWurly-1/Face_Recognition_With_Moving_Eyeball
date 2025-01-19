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

def senddata(serial_device, data, digits=3):
# eyes closed   ser1.write(b'<000,000,090,090>') 
# eyes open     ser1.write(b'<000,000,070,055>')
    first = True
    myString = ""
    for d in data:
        if first == True:
            myString = "<"
            first = False
        else:
            myString += ","
        myString += str(d).zfill(digits)
    myString += ">"
    try:
        serial_device.write(myString.encode())
#        print(myString)
    except:
        print("Data transmission failed")

if __name__ == "__main__":
    
#    ser1 = initConnection('/dev/ttyUSB0', 115200)
#    ser1 = initConnection('/dev/ttyCH341USB0', 115200)
    ser1 = initConnection('COM9', 115200)

    while(True):
        senddata(ser1 , [0, 0, 90, 90])
        time.sleep(1) 
        
        senddata(ser1 , [10, 10, 70, 55])
        time.sleep(1)
