# Face_Recognition_Doorcam
This is a set of modified python programs that can be executed on a Win10 PC, Raspberry Pi or Jetson Nano.
They enable: 
- Face recognition
- Speech output via a USB speaker
- USB Serial comms
N.B. A separate Arduino board is connected by USB - This Arduino is used just to control 2 servos. These servos move an Eyeball such the eyeball always moves to look at the person's face.   

Please note: Credits for the original program goes to Adam Geitgey. For more info, please follow this link
https://medium.com/@ageitgey/build-a-hardware-based-face-recognition-system-for-150-with-the-nvidia-jetson-nano-and-python-a25cb8c891fd 

The changes I have done are
 - Create a version of the "doorcam.py" program, so that it handles names for the images, outputs speech and sends UART messages to control pan and tilt servos.
 - Create an Arduino program called "JETSON_NANO_SERIAL_RECEIVE" which deciphers 2 numeric values from UART messages and uses them to control the position of 2 servos   
 - Create a  python program  called "amend_pics.py" which is used to manage the images harvested by the "doorcam.py" program i.e. images can be renamed or deleted. Whatever name is given to the image, the speech processing part uses it to speak the name of the image whenever it is recognised.   

# SETUP

You will need to do the following 
 - On your device (Win10 PC or SBC), open a terminal and execute the basic install e.g.
   - Follow instructions from https://medium.com/@ageitgey/build-a-hardware-based-face-recognition-system-for-150-with-the-nvidia-jetson-nano-and-python-a25cb8c891fd In summary it is
     - sudo apt-get update
     - sudo apt-get upgrade 
     - sudo apt-get install python3-pip
     - sudo apt-get install espeak
     - sudo pip3 install pyttsx3
     - sudo pip3 install gTTs
     - Install either of these
       - sudo pip3 install playsound     (Win10 or Jetson Nano)
       - sudo apt install mpg123         (This is needed for a R.PI) 
     - SERIAL comms
       - pip3 install pyserial
       - The following only for Jetson Nano or R.Pi (Win10 is OK)
         - sudo chmod 666 /dev/ttyUSB0
         - sudo adduser pete dialout
     - NANO text editor (Jetson Nano only)
       - sudo apt-get install nano
     - FACE RECOGNITION - From https://medium.com/@ageitgey/build-a-face-recognition-system-for-60-with-the-new-nvidia-jetson-nano-2gb-and-python-46edbddd7264
       - sudo apt-get install python3-pip cmake libopenblas-dev liblapack-dev libjpeg-dev
       - sudo pip3 -v install Cython face_recognition

     - VSCODE - Do either of these
       - For win10 
         - Install VSCode from https://code.visualstudio.com/download
         - Download for Win10 and install it
       - For Jetson nano
         - Install VSCode from https://code.visualstudio.com/download
         - Download the ".deb" file called  "ARM 64"
         - Double click what you download - you can then install it
         - Use "Search" to find the icon and attach to desktop for easy access
       - For R.Pi 
         - Download and use Pycharm
       

- On your device, attach a standard USB Webcam (Logitech 922 is recommended)

# Running
 - On your device, open a terminal 
   - CD to the folder where the programs have been stored
   - Execute "python3 Doorcam.py" (you may have to use "python Doorcam.py")
     - Let the program capture your face (you will see this being reported in the new "video" window that pops up)
     - Wait for the file to be saved (in the terminal, you will see a message saying when this has been done)
     - Stop the program 
   - Execute "python3 amend_pics.py"  
     - The program will go through each image, display it in a popup window, and the terminal will prompt you to enter a new name for the image  
     - Enter a name for the image and press enter e.g. if it was you, enter your name
     - When all captured images have been processed, the program will store the changes to the db file, and exit processing
   - Wait 5 mins and then execute "python3 Doorcam.py" for the 2nd time (N.B. you have to wait 5 mins for a timeout in the program to expire)
     - When the program recognises you. it will now speak and say "Hi xxxx, Nice to see you" where xxxx is the name you assigned to the image. N.B. It will only say it on "new visits" - look in the code to understand how the timing works for this   
