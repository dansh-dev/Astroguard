import cv2
import numpy as np
import time
import os
import threading

import os
os.environ["QT_QPA_PLATFORM"] = "xcb"

# A lock to prevent concurrent access to the camera, ensuring thread safety
camera_lock = threading.Lock()

# Load the pre-trained Haar Cascade model, which is used for detecting faces in an image
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Function to determine if a detected face is centered within the frame
def is_centered(face, frame_width, frame_height):
    x, y, w, h = face
    # Calculate the center coordinates of the detected face
    face_center_x = x + w // 2
    face_center_y = y + h // 2
    # Calculate the center coordinates of the camera frame
    frame_center_x = frame_width // 2
    frame_center_y = frame_height // 2
    # Define how much deviation is allowed from the center before it's considered off-center
    tolerance_x = frame_width // 10
    tolerance_y = frame_height // 10
    # Check if the face is within the acceptable range of the frame's center
    return (abs(face_center_x - frame_center_x) < tolerance_x) and (abs(face_center_y - frame_center_y) < tolerance_y)

# Function to capture a photo with the webcam
def take_picture(filename):
    with camera_lock:
        cap = cv2.VideoCapture(0)  # Open the webcam
        if not cap.isOpened():
            raise Exception("Unable to access the webcam")

        try:
            # Set the camera resolution to 1920x1080 pixels
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            while True:
                # Capture a frame from the webcam
                ret, frame = cap.read()
                if not ret:
                    break

                frame2 = frame
                # Convert the captured frame to grayscale for face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Use the Haar Cascade classifier to detect faces in the grayscale image
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                # Obtain the dimensions of the captured frame
                frame_height, frame_width = frame.shape[:2]

                # Iterate over each detected face
                for (x, y, w, h) in faces:
                    # Check if the face is centered within the frame
                    if is_centered((x, y, w, h), frame_width, frame_height):
                        # Start a countdown before taking the picture
                        for i in range(7, 0, -1):
                            ret, frame = cap.read()
                            if not ret:
                                break
            
                            cv2.waitKey(1000)  # Wait for 1 second before continuing the countdown

                        # Save the captured frame as an image file with the provided filename
                        image_path = os.path.join('faces', f'{filename}.png')
                        cv2.imwrite(image_path, frame)
                        return image_path

                # Exit the loop if the 'q' key is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            # Always release the camera and close any open windows, even if an error occurs
            cap.release()
            cv2.destroyAllWindows()

    return None
