import face_recognition
import cv2
import os
import numpy as np
import time

# Directory containing the known faces
faces_directory = 'faces'

# Initialize an array for known face encodings and their names
known_face_encodings = []
known_face_names = []

# Load all the images from the 'faces' directory

# Function to capture an image using a webcam
def capture_image_from_webcam():
    # Open a connection to the webcam
    video_capture = cv2.VideoCapture(0)

    # Warm up the camera for 5 seconds to allow auto-adjustment
    start_time = time.time()
    while time.time() - start_time < 5:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to read from webcam.")
            return None

    # Capture a single frame after the warm-up period
    ret, frame = video_capture.read()
    
    # Release the webcam
    video_capture.release()
    
    # If a frame was captured, save it
    if ret:
        image_path = "captured_image.jpg"
        cv2.imwrite(image_path, frame)
        return image_path
    else:
        print("Failed to capture image.")
        return None

# Function to recognize faces in the captured image
def recognize_faces_in_image(image_path):
    # Load the image to recognize
    image_to_recognize = face_recognition.load_image_file(image_path)
    
    # Find all faces and their encodings in the image
    face_locations = face_recognition.face_locations(image_to_recognize)
    face_encodings = face_recognition.face_encodings(image_to_recognize, face_locations)
    
    recognized_names = []

    # Iterate over each face found in the image
    for face_encoding in face_encodings:
        # See if the face is a match for the known faces
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        
        # Use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
        
        recognized_names.append(name)

    return recognized_names

def recognize():
    for filename in os.listdir(faces_directory):
        if filename.endswith(".jpg") or filename.endswith(".png"):  # Adjust file extensions as needed
            # Load the image
            image_path = os.path.join(faces_directory, filename)
            print(image_path)
            image = face_recognition.load_image_file(image_path)
            
            # Encode the face(s) in the image
            face_encodings = face_recognition.face_encodings(image)
            
            # There might be multiple faces in an image; handle each one
            for face_encoding in face_encodings:
                known_face_encodings.append(face_encoding)
                # Use the filename (minus the extension) as the person's name
                known_face_names.append(os.path.splitext(filename)[0])

    captured_image_path = capture_image_from_webcam()
    if captured_image_path:
        recognized_people = recognize_faces_in_image(captured_image_path)
        return recognized_people
    else:
        recognized_people = []
        return recognized_people
