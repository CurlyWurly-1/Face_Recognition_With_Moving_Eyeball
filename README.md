# Face_Recognition_Doorcam
These python programs can be executed on any of the following devices. 
- Win10 PC
- Raspberry Pi
- Jetson Nano.

For whatever device you choose, consider that there are some device specific instructions you need to follow, but these are all identified in the section below called "Setup". 

The execution of these programs enable: 
- Face recognition from video images seen from a Webcam
- Speech output (On a Jetson Nano, you have to use a USB speaker)
- USB Serial comms via USB - The data that is sent contains the "X" and "Y" head position co-ordinates. N.B. An arduino can be used here to read these co-ordinates so that an eyeball/servo unit can be controlled. The Arduino program code is included in this repo and it is called "JETSON_NANO_SERIAL_RECEIVE.ino". The arduino board is connected to your device via a USB cable and once it receives the USB serial data, the arduino board code translates it to servo positions so that signals to the eyeball/servo unit. The eyeball moves and gives the illusion that whenever a user's face is recognised, the eyeball moves and looks at the users face - spooky. 

N.B. Please note: Credits for the original "Doorcam.py" program goes to Adam Geitgey. For more info, please follow this link
https://medium.com/@ageitgey/build-a-hardware-based-face-recognition-system-for-150-with-the-nvidia-jetson-nano-and-python-a25cb8c891fd 

The changes which I have applied include:
 - Create a  python program called "doorcam.py", which is cloned from Adam's code, but amended to handle image names, speech output and UART messaging (To control 2 servos in a dual axis assembly - panning and tilting). 
 - Create a  python program called "SerialModule.py" to control the UART communication 
 - Create a  python program called "speak.py" to control speach output (To use speech, you need to have an internet connection)  
 - Create a  python program  called "amend_pics.py" which is used to manage the images harvested by the "doorcam.py" program i.e. images can be renamed or deleted. Whatever name is given to the image, the speech processing part uses it to speak the name of the image whenever it is recognised.   
 - Create an Arduino program called "JETSON_NANO_SERIAL_RECEIVE" which deciphers 2 numeric values from UART messages and uses them to control the position of 2 servos 

The 2GB Jetson nano will work, but if you want acceptable performance, you are better off getting a Xavier NX or AGX. This allows you to set a lower value for "detectScope" which means a face can be recognised further away from the camera. The problem with doing this is that to double the performance, it seems you have to spend 5 times as much on the device!!

 
 - for a Xavier AGX, setting the "DetectScope" variable to a value of 1.5 -   allows for 5 frames per second,  with recognition starting about 4 metres from the camera
 - for a Jetso Nano (2GB), setting the "DetectScope" variable to a value of 2.5 -   allows for 3.5 frames per second,  with recognition starting about 1.5 metres from the camera

# SETUP

You will need to do the following 
 - On your device (Win10 PC or SBC), attach a standard USB Webcam (Logitech 922 is recommended)
 - On your device (Win10 PC or SBC), install software 
   - For win10
     - Download and install latest "python" (3.11?) from https://www.python.org/downloads/ 
     - Download and install "VSCode" from https://code.visualstudio.com/download
     - Download and install "Visual Studio (Community)" **and ensure you add "visual studio desktop development with c++"** from https://visualstudio.microsoft.com/downloads/ 
     - Open an elevated CMD terminal (administrator mode) and execute the following commands 
       - pip install pyttsx3
       - pip install gTTs
       - pip install playsound
       - pip install pyserial
       - pip install opencv-python
       - py -m pip install cmake
       - git clone https://github.com/davisking/dlib
       - cd dlib
       - py setup.py install
       - pip install face-recognition
   - For Jetson Nano
     - Follow instructions from https://medium.com/@ageitgey/build-a-hardware-based-face-recognition-system-for-150-with-the-nvidia-jetson-nano-and-python-a25cb8c891fd In summary it is
       - sudo apt-get update
       - sudo apt-get upgrade 
       - sudo apt-get install python3-pip
       - sudo apt-get install espeak
       - sudo pip3 install pyttsx3
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
