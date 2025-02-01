import face_recognition
import cv2
import pickle
import numpy as np
import time
import collections
from datetime import datetime, timedelta
from math import degrees, atan
from subprocess import Popen
import SerialModule as sv
from gtts import gTTS
from playsound import playsound

# Accessing the camera with OpenCV on a laptop just requires passing in the number of the webcam (usually 0)
# Note: You can pass in a filename instead if you want to process a video file instead of a live camera stream  
# N.B.  With DETECTSCALE = 2.5 and FRAME_WIDTH/FRAME_HEIGHT = 1280/720   -> FPS = 10
# N.B.  With DETECTSCALE = 1   and FRAME_WIDTH/FRAME_HEIGHT = 1280/720   -> FPS = 7.5

# Camera resolution configuration
FRAME_WIDTH, FRAME_HEIGHT = 1280, 720
DETECT_SCALE = 2.5                      # Lower means more detail but slower

# Servo middle positions (These two values are for "eye" tuning )
MIDPOINT_UPDOWN    = 55
MIDPOINT_LEFTRIGHT = 79

# Number of frames to average over when calcualting the FPS value (Frames Per Second)
FPS_AVERAGE_WINDOW = 10  

# Set this flag to True if using Raspberry Pi or Jetson Nano CSI Camera Module
USING_RPI_CAMERA_MODULE = False  # Change to True if using a Raspberry Pi/Jetson Nano camera

# Global Face Data
known_face_encodings = []
known_face_metadata = []
fps_values = collections.deque(maxlen=FPS_AVERAGE_WINDOW)  # Circular buffer for FPS


#****************************************************************************************************
# get_jetson_gstreamer_source
#****************************************************************************************************
def get_jetson_gstreamer_source(width=FRAME_WIDTH, height=FRAME_HEIGHT):
    """Returns GStreamer pipeline for Jetson Nano camera with specified width and height."""
    return (
        f"nvarguscamerasrc ! video/x-raw(memory:NVMM), width={width}, height={height}, framerate=30/1 ! "
        f"nvvidconv flip-method=2 ! video/x-raw, width={width}, height={height}, format=(string)BGRx ! "
        "videoconvert ! video/x-raw, format=(string)BGR ! appsink"
    )

#****************************************************************************************************
# say_background 
#****************************************************************************************************
def say_background(text):
    """Run speech synthesis in the background."""
    Popen(['python', 'speak.py', text])  # For Windows

#****************************************************************************************************
# save_known_faces 
#****************************************************************************************************
def save_known_faces():
    """Save known faces to a file."""
    with open("known_faces.dat", "wb") as file_out:
        pickle.dump([known_face_encodings, known_face_metadata], file_out)
    print("Known faces saved.")

#****************************************************************************************************
# load_known_faces 
#****************************************************************************************************
def load_known_faces():
    """Load known faces from a file."""
    global known_face_encodings, known_face_metadata
    try:
        with open("known_faces.dat", "rb") as file_in:
            known_face_encodings, known_face_metadata = pickle.load(file_in)
        print("Loaded known faces.")
    except (FileNotFoundError, EOFError):
        print("No previous face data found.")
        known_face_encodings, known_face_metadata = [], []

#****************************************************************************************************
# register_new_face
#****************************************************************************************************
def register_new_face(face_encoding, face_image):
    """Add a new face to the list of known faces."""
    known_face_encodings.append(face_encoding)
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
    """Check if a face is already in the database."""
    if not known_face_encodings:
        return None, False

    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
    best_match_idx = np.argmin(face_distances)

    if face_distances[best_match_idx] < 0.65:
        metadata = known_face_metadata[best_match_idx]
        metadata["last_seen"] = datetime.now()
        metadata["seen_frames"] += 1
        
        new_visit = datetime.now() - metadata["first_seen_this_interaction"] > timedelta(minutes=1)
        if new_visit:
            metadata["first_seen_this_interaction"] = datetime.now()
            metadata["seen_count"] += 1
        return metadata, new_visit
    return None, False

#****************************************************************************************************
#  calculate_fps
#****************************************************************************************************
def calculate_fps(prev_time):
    """Calculates FPS and maintains an average over recent frames."""
    current_time = time.time()
    fps = 1.0 / (current_time - prev_time) if prev_time else 0
    fps_values.append(fps)
    
    avg_fps = sum(fps_values) / len(fps_values)  # Compute average FPS
    return avg_fps, current_time


#****************************************************************************************************
# Main Loop
#****************************************************************************************************
def main_loop():
    """Main face recognition loop."""
    global ser1
    frame_names, recent_visitor_names = [], []
    faces_since_last_save = 0
    prev_time = time.time()

    print("Camera activated. Press 'q' to exit.")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to capture frame.")
            break

        small_frame = frame if DETECT_SCALE == 1 else cv2.resize(frame, (0, 0), fx=1/DETECT_SCALE, fy=1/DETECT_SCALE)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame, model="cnn")
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_labels = []
        for face_loc, face_enc in zip(face_locations, face_encodings):
            metadata, new = lookup_known_face(face_enc)
            face_name = metadata["face_name"] if metadata else "New visitor!"
            
            if new and face_name not in frame_names and face_name not in recent_visitor_names:
                say_background(f"Hi {face_name}, Nice to see you")
                frame_names.append(face_name)

            face_labels.append(f"{face_name} at door")

            if not metadata:
                top, right, bottom, left = face_loc
                face_image = cv2.resize(small_frame[top:bottom, left:right], (150, 150))
                register_new_face(face_enc, face_image)

        # Draw face boxes
        for (top, right, bottom, left), label in zip(face_locations, face_labels):
            top, right, bottom, left = [int(x * DETECT_SCALE) for x in (top, right, bottom, left)]
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, label, (left, bottom - 10), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
            FaceMidDiffPan  = ( left   + ( ( right - left   ) / 2 ) - ( FRAME_WIDTH  / 2 ) ) * 45 / ( FRAME_WIDTH  / 2 )  
            FaceMidDiffTilt = ( bottom + ( ( top   - bottom ) / 2 ) - ( FRAME_HEIGHT / 2 ) ) * 45 / ( FRAME_HEIGHT / 2 )
            pan  = MIDPOINT_LEFTRIGHT - degrees(atan(FaceMidDiffPan  / 90 ) )  # 79 is midpoint Horizontal - lower and it points its right (your left)
            tilt = MIDPOINT_UPDOWN + degrees(atan(FaceMidDiffTilt / 90 ) )  # 55 is midpoint vertical   - lower means it points more up
            lr = int((int(pan - MIDPOINT_LEFTRIGHT )) / 1.5 )
            ud = int( (int(0 - (tilt - MIDPOINT_UPDOWN ))) / 3 ) 
#######################################################################################
            sv.senddata(ser1 , [int(lr), int(ud), 70, 55] )
#######################################################################################

        # Display recent visitors
        recent_visitor_names = []
        for metadata in known_face_metadata:
            if datetime.now() - metadata["last_seen"] < timedelta(seconds=10) and metadata["seen_frames"] > 5:
                x_pos = len(recent_visitor_names) * 150
                frame[30:180, x_pos:x_pos + 150] = metadata["face_image"]
                recent_visitor_names.append(metadata["face_name"])
                visits = metadata["seen_count"]
                cv2.putText(frame, f"{metadata['face_name']} - {visits} visits", (x_pos + 10, 170), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

        # Calculate average FPS and show on screen
        avg_fps, prev_time = calculate_fps(prev_time)
        cv2.putText(frame, f"FPS: {avg_fps:.1f}", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        cv2.imshow("Face Recognition", frame)

        # Check if to exit        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            save_known_faces()
            break

        faces_since_last_save += 1
        if faces_since_last_save > 100:
            save_known_faces()
            faces_since_last_save = 0

    ser1.close()
    video_capture.release()
    cv2.destroyAllWindows()

#****************************************************************************************************
# Program Entry Point
#****************************************************************************************************
if __name__ == "__main__":

# Attempt to connect
    ser1 = sv.find_and_connect_serial()
#    ser1 = sv.initConnection('COM9', 115200)

# Initialize Video Capture
    if USING_RPI_CAMERA_MODULE:
        video_capture = cv2.VideoCapture(get_jetson_gstreamer_source(), cv2.CAP_GSTREAMER)
    else:
        video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow for Windows optimization
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    # Verify that the camera was opened successfully
    if not video_capture.isOpened():
        print("Error: Could not open video capture.")
    else:
        print(f"Video capture initialized with resolution {FRAME_WIDTH}x{FRAME_HEIGHT}")

    load_known_faces()
    
    main_loop()
