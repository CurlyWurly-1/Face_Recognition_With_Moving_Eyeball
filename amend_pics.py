import face_recognition
import cv2
from datetime import datetime, timedelta
import numpy as np
import platform
import pickle

# Our list of known face encodings and a matching list of metadata about each face.
known_face_encodings = []
known_face_metadata = []
new_known_face_encodings = []
new_known_face_metadata = []

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
        print("")
        print("Known faces backed up to disk - End of program.")


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
    print("")
    print("Trying to load faces from disk.....")
    try:
        with open("known_faces.dat", "rb") as file1_connection_in:
            known_face_encodings, known_face_metadata = pickle.load(file1_connection_in)
            print("faces loaded OK")
    except FileNotFoundError as e:
        print("No previous face data found - starting with a blank known face list.")
        pass


#****************************************************************************************************
# main_loop
#****************************************************************************************************
def main_loop():
 
    global known_face_encodings, known_face_metadata

    load_known_faces()

    for metadata, encodings in zip(known_face_metadata, known_face_encodings):
        try:
            face_label = f"{metadata['face_name']}"
        except KeyError as e:
            face_label = '?'
            pass
        frame = metadata['face_image']
        # Show image
        cv2.imshow('Picture', frame)
        cv2.waitKey(500)
        # Prompt for name change
        print("")
        print(f"This image is called '{face_label}'" )
        print(f"- To SKIP              : Just press ENTER" )
        print(f"- To RENAME            : Type the new name here, and press ENTER" )
        print(f"- To MARK FOR DELETION : Type 0, and then press ENTER" ) 
        val = input("Skip / Rename / Delete? :   ")
        # If a name has been typed, save it 
        if val != '': 
            metadata['face_name'] = val
        if val != '0':
            new_known_face_metadata.append(metadata) 	
            new_known_face_encodings.append(encodings)
        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        known_face_encodings = new_known_face_encodings
        known_face_metadata  = new_known_face_metadata

    save_known_faces()
    

#****************************************************************************************************
# S T A R T   O F   P R O G R A M
#****************************************************************************************************
if __name__ == "__main__":
    main_loop()
