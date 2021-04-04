# Face_Recognition_Doorcam
This is a set of modified python programs that allow face recognition and speech output. You can use these python programs in a Win10 PC, Raspberry Pi or Jetson Nano.

Please note: Credits for the original program goes to Adam Geitgey. For more info, please follow this link
https://medium.com/@ageitgey/build-a-hardware-based-face-recognition-system-for-150-with-the-nvidia-jetson-nano-and-python-a25cb8c891fd 

The changes I have done are
 - Modify the "doorcam.py" program to handle names for the images and output speech. 
 - Create "amend_pics.py" which can be used to update the name assigned to each image that was automatically captured by "doorcam.py"  

# SETUP

You will need to do the following 
 - On your device (Win10 PC or SBC), open a terminal and execute the basic installs e.g.
   - Install VSCode from https://code.visualstudio.com/
   - Follow instructions from https://www.murtazahassan.com/face-recognition-opencv/
   - Follow instructions from https://medium.com/@ageitgey/build-a-hardware-based-face-recognition-system-for-150-with-the-nvidia-jetson-nano-and-python-a25cb8c891fd
   - Download the two programs in this repository to a folder 
- On your device, attach a standard USB Webcam (Logitech 922 is recommended)

# Running
 - Execute VSCode 
   - Open the folder where the programs have been stored
   - Double click "Doorcam.py" on the left, and when the code is displayed on the right, execute it byu pressing the green triangle. 
     - Let the program capture your face (you will see this being reported in the video)
     - Wait for the file to be saved (you will see a message in the terminal)
     - Stop the program 
   - Double-click "amend_pics.py" on the left, and when the code is displayed on the right, execute it by pressing the green triangle. 
     - The program will list each captured image and the terminal will prompt you to enter a new name for the image  
     - Enter a name for the image and press enter
     - When all catured images have been porcessed, the program will end
   - Wait 5 mins and then double-click "Doorcam.py" on the left for the 2nd time (you have to wait 5 mins for a timeout in the program to expire)
     - The program will now recognise you and when it does - it will say your "Hi xxxx, Nice to see you" but it will only say it on a "new visit"   
