import face_recognition
import cv2
from datetime import datetime, timedelta
from math import *
import numpy as np
import platform
import pickle
import os
import SerialModule as sv
from subprocess import Popen
import time

from gtts import gTTS
from playsound import playsound
#import pyttsx3

# Set this depending on your camera type:
# - True = Raspberry Pi 2.x camera module
# - False = USB webcam or other USB video input (like an HDMI capture device)
USING_RPI_CAMERA_MODULE = False

# Our list of known face encodings and a matching list of metadata about each face.
known_face_encodings = []
known_face_metadata = []



#****************************************************************************************************
# say_background
#****************************************************************************************************
def say_background(text):
#    p1 = Popen(['python', 'speak.py', text,])    # For windows
    p1 = Popen(['python3', 'speak.py', text,])    # For Jetson Nano


#****************************************************************************************************
# say_foreground
#****************************************************************************************************
def say_foreground(name):
    try:
        os.remove("welcome1.mp3")
    except:
        pass
    text = 'Hi' + name + ', Nice to see you!'
    language = 'en'
    myobj = gTTS(text=text, lang=language, slow=False)
    myobj.save("welcome1.mp3")
    playsound("welcome1.mp3")
    os.remove("welcome1.mp3")

#****************************************************************************************************
# save_known_faces
#****************************************************************************************************
def save_known_faces():
# N.B. The command "global" DOES NOT need to be specified in this method.
# This is because the global objects are only being referred to i.e. They are NEVER on the left hand side of any assignment command in this method. 
# This means that the compiler will decide that objects "known_face_encodings" and "known_face_metadata" 
# are NOT required to be be created/cloned/used as completely separate local variables with the same name 


# This "with open" command does the following:
#  A connection to a physical file called “known_faces.dat” is opened as an object called “file1_connection_out“ in "write-only" mode 
#  Another object called "file_data" is (temporarily) created which carries data clubbed from the two main global objects called "known_face_encodings" and "known_face_metadata"
#  The object "file_data" is output via connection "file1_connection_out" (which points to physical file “known_faces.dat”)
#  N.B. The option "wb" means 
#           "Open a write-only file in binary mode".
    with open("known_faces.dat", "wb") as file1_connection_out:
        file_data = [known_face_encodings, known_face_metadata]
        pickle.dump(file_data, file1_connection_out)
        print("Known faces backed up to disk.")


#****************************************************************************************************
# load_known_faces
#****************************************************************************************************
def load_known_faces():

# The command "global" DOES need to be used in this method.
# This is because the global objects "known_face_encodings" and "known_face_metadata" are to be updated in this method. 
# i.e. They ARE SEEN on the left hand side of an assignment command in this method.
# If "global" was not used to tag the variables, Then any of these variables that appear on the left of assignment commands 
# would trigger the compiler to ignore the global variable of that name, and instead create temporary variables of the same name 
# which would be use within this method instead of the global versions 
# IMO, this is a very annoying and stupid "freedom" in Python - the local versions could even be completely different types
#      - what a crock of sh*t for mistake error trapping !! 
    global known_face_encodings, known_face_metadata

# This "with open" command does the following:
#  A connection to a physical file called “known_faces.dat” is opened as an object called “file1_connection_in“ in "read binary" mode  
#  The data of the file referenced via connection "file1_connection_in" is overwritten into global objects "known_face_encodings" and "known_face_metadata"
#  N.B. The option "rb" means 
#       "Open the file as read-only in binary format and start reading from the beginning of the file. 
#        While binary format can be used for different purposes, it is usually used when dealing with 
#        things like images and videos"
    try:
        with open("known_faces.dat", "rb") as file1_connection_in:
            known_face_encodings, known_face_metadata = pickle.load(file1_connection_in)
            print("Known faces loaded from disk.")
    except FileNotFoundError as e:
        print("No previous face data found - starting with a blank known face list.")
        pass


#****************************************************************************************************
# get_jetson_gstreamer_source
#   This method is NOT needed if you are using a webcam. 
#   This method is only used if you are using he R.PI camera
#****************************************************************************************************
def get_jetson_gstreamer_source(capture_width=1280, capture_height=720, display_width=1280, display_height=720, framerate=60, flip_method=0):

    """
    Return an OpenCV-compatible video source description that uses gstreamer to capture video from the RPI camera on a Jetson Nano
    """
    return (
            f'nvarguscamerasrc ! video/x-raw(memory:NVMM), ' +
            f'width=(int){capture_width}, height=(int){capture_height}, ' +
            f'format=(string)NV12, framerate=(fraction){framerate}/1 ! ' +
            f'nvvidconv flip-method={flip_method} ! ' +
            f'video/x-raw, width=(int){display_width}, height=(int){display_height}, format=(string)BGRx ! ' +
            'videoconvert ! video/x-raw, format=(string)BGR ! appsink'
            )


#****************************************************************************************************
# register_new_face
#****************************************************************************************************
def register_new_face(face_encoding, face_image):
    """
    Add a new person to our list of known faces
    """
    # Add the face encoding to the list of known faces
    known_face_encodings.append(face_encoding)
    # Add a matching dictionary entry to our metadata list.
    # We can use this to keep track of how many times a person has visited, when we last saw them, etc.
    known_face_metadata.append({
        "face_name": "?",
        "first_seen": datetime.now(),
        "first_seen_this_interaction": datetime.now(),
        "last_seen": datetime.now(),
        "seen_count": 1,
        "seen_frames": 1,
        "face_image": face_image,
    })


#****************************************************************************************************
# lookup_known_face
#****************************************************************************************************
def lookup_known_face(face_encoding):
    """
    See if this is a face we already have in our face list
    """
    metadata = None
    new = False

    # If our known face list is empty, just return nothing since we can't possibly have seen this face.
    if len(known_face_encodings) == 0:
        return metadata, new

    # Calculate the face distance between the unknown face and every face on in our known face list
    # This will return a floating point number between 0.0 and 1.0 for each known face. The smaller the number,
    # the more similar that face was to the unknown face.
    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

    # Get the known face that had the lowest distance (i.e. most similar) from the unknown face.
    best_match_index = np.argmin(face_distances)

    # If the face with the lowest distance had a distance under 0.6, we consider it a face match.
    # 0.6 comes from how the face recognition model was trained. It was trained to make sure pictures
    # of the same person always were less than 0.6 away from each other.
    # Here, we are loosening the threshold a little bit to 0.65 because it is unlikely that two very similar
    # people will come up to the door at the same time.
    if face_distances[best_match_index] < 0.65:
        # If we have a match, look up the metadata we've saved for it (like the first time we saw it, etc)
        metadata = known_face_metadata[best_match_index]

        # Update the metadata for the face so we can keep track of how recently we have seen this face.
        metadata["last_seen"] = datetime.now()
        metadata["seen_frames"] += 1

        # We'll also keep a total "seen count" that tracks how many times this person has come to the door.
        # But we can say that if we have seen this person within the last 5 minutes, it is still the same
        # visit, not a new visit. But if they go away for awhile and come back, that is a new visit.
        if datetime.now() - metadata["first_seen_this_interaction"] > timedelta(minutes=1):
            metadata["first_seen_this_interaction"] = datetime.now()
            metadata["seen_count"] += 1
            new = True
        else:
            new = False

    return metadata, new


#****************************************************************************************************
# main_loop
#****************************************************************************************************
def main_loop():
    global ser1
    # Get access to the webcam. The method is different depending on if you are using a Raspberry Pi camera or USB input.
    if USING_RPI_CAMERA_MODULE:
        # Accessing the camera with OpenCV on a Jetson Nano requires gstreamer with a custom gstreamer source string
        video_capture = cv2.VideoCapture(get_jetson_gstreamer_source(), cv2.CAP_GSTREAMER)
    else:
        # Accessing the camera with OpenCV on a laptop just requires passing in the number of the webcam (usually 0)
        # Note: You can pass in a filename instead if you want to process a video file instead of a live camera stream
        detectScale = 2.5        # Higher means more detail but slower
#        frameWidth  = 1280
#        frameHeight = 720
        frameWidth  = 800
        frameHeight = 600

        video_capture = cv2.VideoCapture(0)
#        video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)     # Use this for windows
        video_capture.set(3, frameWidth)
        video_capture.set(4, frameHeight)

    # Track how long since we last saved a copy of our known faces to disk as a backup.
    number_of_faces_since_save = 0
    pTime = 0

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=(1/detectScale), fy=(1/detectScale))

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
#        rgb_small_frame = small_frame[:, :, ::-1]
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Find all the face locations and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame, 1, "cnn")   # This is for Jetson or CUDA enabled win10 PCs
#        face_locations = face_recognition.face_locations(rgb_small_frame)
        
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        # Loop through each detected face and see if it is one we have seen before
        # If so, we'll give it a label that we'll draw on top of the video.
        face_labels = []
        new = False
        for face_location, face_encoding in zip(face_locations, face_encodings):
            # See if this face is in our list of known faces.
            metadata, new = lookup_known_face(face_encoding)

            # If we found the face, label the face with some useful information.
            if metadata is not None:
                time_at_door = datetime.now() - metadata['first_seen_this_interaction']
                activeSeconds = int(time_at_door.total_seconds())
                try:
                    face_name = f"{metadata['face_name']}"
                except KeyError as e:
                    face_name = '?'
                    pass
                if new is True:
                    say_background("Hi " + face_name +", Nice to see you")

                face_label = f"{face_name} at door {int(time_at_door.total_seconds())}s"

            # If this is a brand new face, add it to our list of known faces
            else:
                face_label = "New visitor!"

                # Grab the image of the the face from the current frame of video
                top, right, bottom, left = face_location
                face_image = small_frame[top:bottom, left:right]
                face_image = cv2.resize(face_image, (150, 150))

                # Add the new face to our known face data
                register_new_face(face_encoding, face_image)

            face_labels.append(face_label)

        # Draw a box around each face and label each face
        for (top, right, bottom, left), face_label in zip(face_locations, face_labels):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top    *= detectScale
            top     = int(top)
            right  *= detectScale
            right   = int(right)
            bottom *= detectScale
            bottom  = int(bottom)
            left   *= detectScale
            left    = int(left)
            FaceMidDiffPan  = ( left   + ( ( right - left   ) / 2 ) - ( frameWidth  / 2 ) ) * 45 / ( frameWidth  / 2 )  
            FaceMidDiffTilt = ( bottom + ( ( top   - bottom ) / 2 ) - ( frameHeight / 2 ) ) * 45 / ( frameHeight / 2 )
            pan  = 79 - degrees(atan(FaceMidDiffPan  / 90 ) )  # 79 is midpoint Horizontal - lower and it points its right (your left)
            tilt = 55 + degrees(atan(FaceMidDiffTilt / 90 ) )  # 83 is midpoint vertical   - lower means it points more up

# ******************************************************
            sv.senddata(ser1 , [int(pan), int(tilt)], 3)
# ******************************************************

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            cv2.putText(frame, face_label, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

        # Display recent visitor images
        number_of_recent_visitors = 0
        for metadata in known_face_metadata:
            # If we have seen this person in the last minute, draw their image
            if datetime.now() - metadata["last_seen"] < timedelta(seconds=10) and metadata["seen_frames"] > 5:
                # Draw the known face image
                x_position = number_of_recent_visitors * 150
                frame[30:180, x_position:x_position + 150] = metadata["face_image"]
                number_of_recent_visitors += 1

                # Label the image with how many times they have visited
                visits = metadata['seen_count']
                try:
                    face_name = f"{metadata['face_name']}"
                except KeyError as e:
                    face_name = '?'
                    pass
                pic_label = f"{face_name}-{visits} visits"
                if visits == 1:
                    pic_label = "First visit"
                cv2.putText(frame, pic_label, (x_position + 10, 170), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

        if number_of_recent_visitors > 0:
            cv2.putText(frame, "Visitors at Door", (5, 18), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

        cTime = time.time()
        fps = 10 / (cTime - pTime)
        pTime = cTime
        cv2.putText(frame, str(int(fps)/10), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        # Display the final frame of video with boxes drawn around each detected fames
        cv2.imshow('DoorCam with speech - press q to stop', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            save_known_faces()
            break

        # We need to save our known faces back to disk every so often in case something crashes.
        if len(face_locations) > 0 and number_of_faces_since_save > 100:
            save_known_faces()
            number_of_faces_since_save = 0
        else:
            number_of_faces_since_save += 1

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()


#****************************************************************************************************
# S T A R T   O F   P R O G R A M
#****************************************************************************************************
if __name__ == "__main__":
    ser1 = sv.initConnection('/dev/ttyUSB0', 9600)
    load_known_faces()
    main_loop()
