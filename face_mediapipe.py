# https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/face_detection.md

import cv2
import mediapipe as mp
import SerialModule as sv
from math import *
import time


mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

webcam = True

# For webcam input:
if webcam:


#    frameWidth  = 1920           # N.B. 1920/1080 -> FPS = 5  with RTX2070 super
#    frameHeight = 1080
    frameWidth  = 1280          # N.B. 1280/720  -> FPS = 10 with RTX2070 super
    frameHeight = 720
#    frameWidth  = 800           # N.B. 800/600   -> FPS = 30 with RTX2070 super
#    frameHeight = 600

#    ser1 = sv.initConnection('/dev/ttyUSB0', 115200) 
    ser1 = sv.initConnection('COM9', 115200)    

#    cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)     # Use this for windows       
    cap.set(3, frameWidth)
    cap.set(4, frameHeight)

    with mp_face_detection.FaceDetection(
        model_selection=0, min_detection_confidence=0.5) as face_detection:
        pTime = time.time()
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_detection.process(image)

            # Draw the face detection annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.detections:
                for detection in results.detections:
#                    ih, iw, _ = image.shape
# Convert normalized coordinates to pixel coordinates
                    x_min = int(detection.location_data.relative_bounding_box.xmin * frameWidth)
                    y_min = int(detection.location_data.relative_bounding_box.ymin * frameHeight)
                    x_max = int((detection.location_data.relative_bounding_box.xmin + detection.location_data.relative_bounding_box.width) * frameWidth)
                    y_max = int((detection.location_data.relative_bounding_box.ymin + detection.location_data.relative_bounding_box.height) * frameHeight)

                    mp_drawing.draw_detection(image, detection)
# Alternative "cv2" method to draw the bounding box on the image (pixel coordinates)
#                    cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                    top     = int(y_max)
                    right   = int(x_max)
                    bottom  = int(y_min)
                    left    = int(x_min)
                    FaceMidDiffPan  = ( left   + ( ( right - left   ) / 2 ) - ( frameWidth  / 2 ) ) * 45 / ( frameWidth  / 2 )  
                    FaceMidDiffTilt = ( bottom + ( ( top   - bottom ) / 2 ) - ( frameHeight / 2 ) ) * 45 / ( frameHeight / 2 )
                    pan  = 79 - degrees(atan(FaceMidDiffPan  / 90 ) )  # 79 is midpoint Horizontal - lower and it points its right (your left)
                    tilt = 55 + degrees(atan(FaceMidDiffTilt / 90 ) )  # 55 is midpoint vertical   - lower means it points more up
                    lr = int((int(pan-78)) / 1.5 )
                    ud = int( (int(0 - (tilt-60))) / 3 ) 
        # ******************************************************
                    sv.senddata(ser1 , [int(lr), int(ud), 70, 55] )
        # ******************************************************

            # Flip the image horizontally for a selfie-view display.
            image2 = cv2.flip(image, 1)
            # Calculate fps and add to image
            cTime = time.time()
            fps = 10 / (cTime - pTime)
            pTime = cTime
            cv2.putText(image2, str(int(fps)/10), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

            cv2.imshow('MediaPipe Face Detection', image2)

        # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) & 0xFF == ord('q'):
               break

    cap.release()

else:

    # For static images:
    IMAGE_FILES = []
    with mp_face_detection.FaceDetection(
        model_selection=1, min_detection_confidence=0.5) as face_detection:
        for idx, file in enumerate(IMAGE_FILES):
            image = cv2.imread(file)
            # Convert the BGR image to RGB and process it with MediaPipe Face Detection.
            results = face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            # Draw face detections of each face.
            if not results.detections:
                continue
            annotated_image = image.copy()
            for detection in results.detections:
                print('Nose tip:')
                print(mp_face_detection.get_key_point(
                    detection, mp_face_detection.FaceKeyPoint.NOSE_TIP))
                mp_drawing.draw_detection(annotated_image, detection)
            cv2.imwrite('/tmp/annotated_image' + str(idx) + '.png', annotated_image)
