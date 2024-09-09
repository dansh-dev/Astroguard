import cv2
import numpy as np
import tensorflow as tf
import base64
import requests

# Load the TFLite model and allocate tensors.
interpreter = tf.lite.Interpreter(model_path='efficientdet_lite0.tflite')
interpreter.allocate_tensors()

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Load label map
with open('labelmap.txt', 'r') as f:
    labels = [line.strip() for line in f.readlines()]

# Initialize webcam feed
cap = cv2.VideoCapture(0)

allowed_labels = ['person', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe']

# Arduino IP address or hostname 
arduino_url = "http://192.168.4.1/upload"

def encode_image_for_lora(image):
    # Encode image as PNG
    _, buffer = cv2.imencode('.png', image)
    # Convert to base64 to ensure binary safety over LoRa or file storage
    encoded_image = base64.b64encode(buffer).decode('utf-8')
    return encoded_image

def send_post_request_to_arduino(label):
    # Create a dictionary with the encoded image and label
    payload = {
        'label': label,
    }
    
    try:
        # Send the POST request to the Arduino with a timeout
        response = requests.post(arduino_url, json=payload, timeout=2)  # Timeout after 2 seconds
        # Check for success
        if response.status_code == 200:
            print(f"Successfully sent {label} detection to Arduino.")
        else:
            print(f"Failed to send data to Arduino. Status code: {response.status_code}")
    except requests.exceptions.Timeout:
        print(f"Request timed out while sending data to Arduino.")
    except Exception as e:
        print(f"Error sending data to Arduino: {e}")


while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break

    # Resize the frame to the size expected by the model
    input_shape = input_details[0]['shape']
    height, width = input_shape[1], input_shape[2]
    img_resized = cv2.resize(frame, (width, height))

    # Convert the image to the expected type
    if input_details[0]['dtype'] == np.uint8:
        input_data = np.expand_dims(img_resized, axis=0).astype(np.uint8)
    else:
        # Normalize image to [0, 1] if model expects float32
        input_data = np.expand_dims(img_resized, axis=0).astype(np.float32) / 255.0

    # Set the tensor to the model input
    interpreter.set_tensor(input_details[0]['index'], input_data)

    # Run inference
    interpreter.invoke()

    # Extract detection results
    boxes = interpreter.get_tensor(output_details[0]['index'])[0]  # Bounding box coordinates
    class_ids = interpreter.get_tensor(output_details[1]['index'])[0]  # Class index
    scores = interpreter.get_tensor(output_details[2]['index'])[0]  # Confidence scores

    # Loop over each detection and draw bounding boxes and labels
    for i in range(len(scores)):
        if scores[i] > 0.5:  # Confidence threshold
            ymin, xmin, ymax, xmax = boxes[i]
            xmin = int(xmin * frame.shape[1])
            xmax = int(xmax * frame.shape[1])
            ymin = int(ymin * frame.shape[0])
            ymax = int(ymax * frame.shape[0])
            class_id = int(class_ids[i])

            # Check if class_id is within bounds
            if class_id < len(labels):
                label = labels[class_id]

                # Ensure bounding box coordinates are valid
                xmin = max(0, xmin)
                ymin = max(0, ymin)
                xmax = min(frame.shape[1], xmax)
                ymax = min(frame.shape[0], ymax)

                # Crop the image
                cropped_image = frame[ymin:ymax, xmin:xmax]

                # Check if cropped image is not empty and the label is in the allowed list
                if cropped_image.size > 0 and label in allowed_labels:
                    try:
                        send_post_request_to_arduino(label)
                    except Exception as e:
                        print(f"Failed to encode or send image: {e}")

                # Draw bounding box and label
                if label in allowed_labels:
                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                    label_text = f'{label}: {int(scores[i] * 100)}%'
                    cv2.putText(frame, label_text, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('Object Detection', frame)

    # Exit loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close any OpenCV windows
cap.release()
cv2.destroyAllWindows()
