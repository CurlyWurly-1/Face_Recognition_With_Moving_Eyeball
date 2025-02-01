import cv2
import mediapipe as mp
import SerialModule as sv
from math import degrees, atan
import time

# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Webcam parameters
FRAME_WIDTH = 1280  # Adjust based on performance needs
FRAME_HEIGHT = 720
SERIAL_PORT = 'COM10'  # Change for Linux: e.g., '/dev/ttyUSB0'
BAUD_RATE = 115200

# Initialize Serial Communication
try:
    ser1 = sv.initConnection(SERIAL_PORT, BAUD_RATE)
except Exception as e:
    print(f"Serial connection failed: {e}")
    ser1 = None  # Avoids crashes if serial fails

# Initialize Webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # CAP_DSHOW for better performance on Windows
cap.set(3, FRAME_WIDTH)
cap.set(4, FRAME_HEIGHT)

# FPS Calculation
prev_time = time.time()

# Face Detection Model
with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty frame.")
            continue

        # Convert to RGB for MediaPipe
        image.flags.writeable = False
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_detection.process(image_rgb)

        # Convert back to BGR for OpenCV display
        image.flags.writeable = True
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        if results.detections:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                x_min = int(bbox.xmin * FRAME_WIDTH)
                y_min = int(bbox.ymin * FRAME_HEIGHT)
                x_max = int((bbox.xmin + bbox.width) * FRAME_WIDTH)
                y_max = int((bbox.ymin + bbox.height) * FRAME_HEIGHT)

                # Draw detection box
                mp_drawing.draw_detection(image, detection)

                # Face Center & Angle Calculation
                face_mid_x = x_min + (x_max - x_min) / 2
                face_mid_y = y_min + (y_max - y_min) / 2
                face_mid_diff_pan = (face_mid_x - FRAME_WIDTH / 2) * 45 / (FRAME_WIDTH / 2)
                face_mid_diff_tilt = (face_mid_y - FRAME_HEIGHT / 2) * 45 / (FRAME_HEIGHT / 2)

                pan = 79 - degrees(atan(face_mid_diff_pan / 90))
                tilt = 55 + degrees(atan(face_mid_diff_tilt / 90))

                lr = int((pan - 78) / 1.5)
                ud = int((0 - (tilt - 60)) / 3)

                # Send data to Serial
                if ser1:
                    sv.senddata(ser1, [lr, ud, 70, 55])

        # FPS Calculation
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time

        # Show image with detections
        image2 = cv2.flip(image, 1)

        # Display FPS on image
        cv2.putText(image2, f"FPS: {fps:.1f}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 255), 3)

        cv2.imshow('MediaPipe Face Detection', image2)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Cleanup
cap.release()
cv2.destroyAllWindows()
