# Face Recognition with speech and head "X" and "Y" position sent via USB serial 
These python programs can be executed on any of the following devices. 
- Win10 PC
- Raspberry Pi
- Jetson Nano.

The execution of these programs enable: 
- Face recognition from video images seen from a Webcam
- Speech output (On a Jetson Nano, you have to use a USB speaker)
- USB Serial comms via USB - The data that is sent contains the "X" and "Y" head position co-ordinates. 

N.B. An Arduino executing "WATCHMAN_servo_control.ino" can be used to read the USB serial data so that an eyeball/servo unit can be controlled. The arduino board is connected to your device via a USB cable, and when USB serial data is received by the arduino program code, the  "X" and "Y" data is translated into rotational servo position data. This rotational position data is sent to the servos in the eyeball/servo unit and this makes the eyeball to move up,down,left or right as appropriate. It gives the illusion that whenever a person's face is recognised, the eyeball moves to look at the person's face which is great, but combine this eyeball movement with the device also saying the person's name (e.g. "hello XXX"), and the effect is quite spooky. 


To install the software, please refer to the section called **SETUP**. There are a few device specific instructions to take note of, but hopefully all is made clear enough to follow. 

To execute the programs, refer to the section called **Running**

N.B. Please note: Credits for the original "Doorcam.py" program goes to Adam Geitgey. For more info, please follow this link
https://medium.com/@ageitgey/build-a-hardware-based-face-recognition-system-for-150-with-the-nvidia-jetson-nano-and-python-a25cb8c891fd 

The changes I have applied, include:
 - Create a  python program called "doorcam.py", which is cloned from Adam's code, but amended to handle image names, speech output and UART messaging (To control 2 servos in a dual axis assembly - panning and tilting). 
 - Create a  python program called "SerialModule.py" to control the UART communication 
 - Create a  python program called "speak.py" to control speach output (To use speech, you need to have an internet connection)  
 - Create a  python program  called "amend_pics.py" which is used to manage the images harvested by the "doorcam.py" program i.e. images can be renamed or deleted. Whatever name is given to the image, the speech processing part uses it to speak the name of the image whenever it is recognised.   
 - Create an Arduino program called "WATCHMAN_servo_control.ino" which deciphers 4 numeric values from UART messages and uses them to control the position of 5 servos 

The performance of a Jetson Orin nano (super) running Ubuntu, is comparable to I5-6400 CPU in a H110M motherboard (released circa 2015) running windows (32GB ram) with a Nvidia RTX2070 super (configured with Cuda and DLIB support for the GPU).
Put it this way, the Jetson Orin nano super is a really nice way to run this stuff

# SETUP

You will need to do the following 
 - On your device (Win10 PC or SBC), attach a standard USB Webcam (Logitech 922 is recommended)
 - On your device (Win10 PC or SBC), install software 
   - For win10 **with a Nvidia GPU** (N.B. RTX2070 super gives good performance) 
     - Download and install "python" 3.9.11 from https://www.python.org/downloads/ 
     - Download and install "VSCode" from https://code.visualstudio.com/download
     - Download and install "Visual Studio Build Tools 2022" from https://visualstudio.microsoft.com/vs/older-downloads/
       **and ensure you select add "Desktop development with C++"**
     - Install CUDA 12.6 from Nvidia (if you are using Nvidia GPU) 
     - Follow this regarding the system variables and the files you need to download/copy to the otehr library 
       - https://medium.com/geekculture/install-cuda-and-cudnn-on-windows-linux-52d1501a8805#3e72
     - Open an elevated CMD terminal (administrator mode) and execute the following commands 
       - pip install pyttsx3
       - pip install gTTs
       - pip install --upgrade setuptools wheel
       - pip install playsound
       - pip install pyserial
       - pip install opencv-python
       - py -m pip install cmake
       - git clone https://github.com/davisking/dlib
       - cd dlib
       - mkdir build
       - cd build
       - cmake .
       - cd ..
       - python setup.py install
       - pip install face-recognition
   - For Jetson Nano / R.Pi (Raspberry Pi)
     - Follow instructions from https://medium.com/@ageitgey/build-a-hardware-based-face-recognition-system-for-150-with-the-nvidia-jetson-nano-and-python-a25cb8c891fd In summary it is
       - sudo apt-get update
       - sudo apt-get upgrade 
       - sudo apt-get install python3-pip
       - sudo apt-get install espeak
       - sudo pip3 install pyttsx3
       - pip3 install PyAudio
       - sudo apt-get install sox
       - sudo apt-get install libsox-fmt-all
       - sudo pip3 install gTTs
       - Install one of these (N.B. It depends on if you are using a Jetson Nano or a R.Pi)
         - For Jetson nano
           - sudo pip3 install playsound  
         - For R.Pi
           - sudo apt install mpg123       
     - SERIAL comms
       - pip3 install pyserial
       - sudo chmod 666 /dev/ttyUSB0
       - sudo adduser pete dialout
     - NANO text editor (Jetson Nano only)
       - sudo apt-get install nano
     - FACE RECOGNITION - From https://medium.com/@ageitgey/build-a-face-recognition-system-for-60-with-the-new-nvidia-jetson-nano-2gb-and-python-46edbddd7264
       - sudo apt-get install python3-pip cmake libopenblas-dev liblapack-dev libjpeg-dev
       - sudo pip3 -v install Cython face_recognition
     - VSCODE - Install one of these (N.B. It depends on if you are using a Jetson Nano or a R.Pi)
       - For Jetson nano
         - Install VSCode from https://code.visualstudio.com/download
         - Download the ".deb" file called  "ARM 64"
         - Double click what you download - you can then install it
         - Use "Search" to find the icon and attach to desktop for easy access
       - For R.Pi 
         - Download and use Pycharm
       

# Running
 - On your device, open a terminal 
   - CD to the folder where the programs have been stored
   - Execute "python3 Doorcam.py" (you may have to use "python Doorcam.py")
     - Let the program capture your face (you will see this being reported in the new "video" window that pops up)
     - Wait for the file to be saved (in the terminal, you will see a message saying when this has been done)
     - Press "q" when the focus is on the video window. This will stop the program 
   - Execute "python3 amend_pics.py"  
     - The program will go through each image, display it in a popup window, and the terminal will prompt you to enter a new name for the image, or if you want to delete it  
     - If you want, enter a name for the image and press enter e.g. if the image is you, enter your name and press enter
     - When all captured images have been processed, the program will store the changes to the db file, and exit processing
   - Wait 5 mins and then execute "python3 Doorcam.py" for the 2nd time (N.B. you have to wait 5 mins for a timeout in the program to expire)
     - When the program recognises you. it will now speak and say "Hi xxxx, Nice to see you" where xxxx is the name you assigned to the image. N.B. It will only say it if you haven't been seen for a while (5 mins) - look in the code to understand how the timing works for this   
