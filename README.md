# Face_Recognition_Doorcam
This is a set of modified python programs that allow face recognition and speech output. You can use these python programs in a Win10 PC, Raspberry Pi or Jetson Nano.

Please note: Credits for the original program goes to Adam Geitgey. For more info, please follow this link
https://medium.com/@ageitgey/build-a-hardware-based-face-recognition-system-for-150-with-the-nvidia-jetson-nano-and-python-a25cb8c891fd 

The changes I have done are
 - Modify the "doorcam.py" program to handle names for the images and output speech. 
 - Create "amend_pics.py" which can be used to update the name assigned to each image that was automatically captured by "doorcam.py"  

# SETUP

You will need to do the following 
 - On your device (Win10 PC or SBC), open a terminal and execute the basic install e.g.
   - Follow instructions from https://medium.com/@ageitgey/build-a-hardware-based-face-recognition-system-for-150-with-the-nvidia-jetson-nano-and-python-a25cb8c891fd
   - Download the two programs in this repository to a folder on your device
- On your device, attach a standard USB Webcam (Logitech 922 is recommended)

# Running
 - On your device, open a terminal 
   - CD to the folder where the programs have been stored
   - Execute "python3 Doorcam.py" (you may have to use "python Doorcam.py")
     - Let the program capture your face (you will see this being reported in the new "video" window that pops up)
     - Wait for the file to be saved (in the terminal, you will see a message saying when this has been done)
     - Stop the program 
   - Execute "python3 amend_pics.py"  
     - The program will go thorugh each image, display it in a popup window and the terminal will prompt you to enter a new name for the image  
     - Enter a name for the image and press enter e.g. if it was you, enter your name
     - When all catured images have been processed, the program will end
   - Wait 5 mins and then execute "python3 Doorcam.py" for the 2nd time (N.B. you have to wait 5 mins for a timeout in the program to expire)
     - When the program recognises you. it will now speak and say "Hi xxxx, Nice to see you" where xxxx is the name you assigned to the image. N.B. It will only say it on "new visits" - look in the code to understand how the timing works for this   
