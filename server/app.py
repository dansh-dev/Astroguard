import time
from flask_socketio import SocketIO, emit
import threading
from flask import Flask, request, jsonify
from pymongo import DESCENDING, MongoClient
from datetime import datetime
from flask_cors import CORS
import os
from face_recog_register import take_picture
from face_recog2 import recognize
from leds import fade_in_out

# Initialize Flask app
app = Flask(__name__)
# Allow CORS requests from any origin
CORS(app, origins="*")

# Setup SocketIO for WebSocket communication
socketio = SocketIO(app, cors_allowed_origins="*")

# MongoDB setup and collection references
client = MongoClient("mongodb://localhost:27017/")
db = client['alarm_db']
sensors = db['sensor_data']
cctv = db['camera_data']
cctv_profiles = db['camera_profiles']
setups = db['setup_data']
alarmState = db['alarm_state']
securityNotifications = db['security_notifications']

# Endpoint for receiving sensor data
@app.route('/input_data', methods=['POST'])
def input_data():
    # Check if request contains JSON
    if request.is_json:
        data = request.get_json()
        print(data)
        currentState = alarmState.find_one(sort=[("Timestamp", DESCENDING)])
        serialNumber = data['SerialNumber']
        sensorType = serialNumber[:2]
        if sensorType == 'SN':
            # Ensure required fields are present
            required_fields = ["SerialNumber", "AlarmState", "TamperState", "Latitude", "Longitude", "Charge", "SignalStrength"]
            if not all(field in data for field in required_fields):
                return jsonify({"error": "Missing required fields"}), 400
            # Get latest system setup from DB
            latest_setup = setups.find_one(sort=[("created_at", DESCENDING)])
            print(latest_setup['sensors'])
            data['Timestamp'] = datetime.utcnow()

            # Validate sensor against setup
            valid_sensor_list = [sensor["serial"] for sensor in latest_setup['sensors']]
            if valid_sensor_list:
                print("Valid sensors:", valid_sensor_list)
                # Insert data if sensor is valid
                if data['SerialNumber'] in valid_sensor_list:
                    sensors.insert_one(data)
                    # Trigger notification if alarm is activated
                    if data['AlarmState'] == True:
                        current_time = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
                        create_security_notification("Sensor Triggered!", "Sensor triggered:" + data['SerialNumber'], 4, current_time)
                    return jsonify({"message": "Data accepted"}), 201
                else:
                    return jsonify({"error": "Sensor not recognized!"}), 400
            else:
                return jsonify({"error": "Sensor not recognized!"}), 400
        if sensorType == 'CN':   
            required_fields = ["SerialNumber", "Label", "Latitude", "Longitude", "Charge", "SignalStrength"]
            if not all(field in data for field in required_fields):
                return jsonify({"error": "Missing required fields"}), 400
            # Get latest system setup from DB
            latest_setup = setups.find_one(sort=[("created_at", DESCENDING)])
            print(latest_setup['sensors'])
            data['Timestamp'] = datetime.utcnow()
            current_time = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
            valid_sensor_list = [sensor["serial"] for sensor in latest_setup['sensors']]
            if valid_sensor_list:
                print("Valid sensors:", valid_sensor_list)
                # Insert data if sensor is valid
                if data['SerialNumber'] in valid_sensor_list:
                    CamProfile = cctv_profiles.find_one(
                        {"SerialNumber": data['SerialNumber']},
                         sort=[{"TimeStamp", -1}]
                    )
                    if CamProfile:
                        if data['Label'] in CamProfile['AllowedLabels']:
                            if currentState['ArmState'] == True:
                                # Alarm Armed
                                cctv.insert_one(data)
                                print("Data accepted and profile is found!")
                                create_security_notification("Camera Triggered!", f"{data['Label']} detected!", 3, current_time)
                                return jsonify({"message": "Data accepted"}), 201            
                            if currentState['ArmState'] == False:
                                cctv.insert_one(data)
                                create_security_notification("Camera Triggered!", f"{data['Label']} detected!", 3, current_time)
                                return jsonify({"message": "Data accepted"}), 201            
                        else:
                            return jsonify({"error": "Label not allowed!"}), 400            
                    else:
                        new_profile = {
                            "SerialNumber": data["SerialNumber"],
                            "AllowedLabels": ["person", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe"],
                            "TimeStamp": datetime.now()
                        }
                        print("No Profile Found, new one being inserted!")
                        cctv_profiles.insert_one(new_profile)    
                        cctv.insert_one(data)

                else:
                    return jsonify({"error": "Sensor not recognized!"}), 400
            else:
                return jsonify({"error": "Sensor not recognized!"}), 400

            return jsonify({"message": "Data accepted"}), 201
    else:
        return jsonify({"error": "Request must be JSON"}), 400

# This route retrieves a camera setup to allow for display
@app.route('/getCamSetup', methods=['POST'])
def getCamSetup():
    if request.method == 'POST':
        data = request.get_json()
        if data and 'SerialNumber' in data:
            CamProfile = cctv_profiles.find_one(
                {"SerialNumber": data['SerialNumber']},
                sort=[{"TimeStamp", -1}]
            )
            CamProfile.pop('_id', None)
            print(CamProfile)
            return jsonify(CamProfile), 200
        else:
            return jsonify({'message': 'SerialNumber missing!'}), 400
    else:
        return jsonify({'message': 'Incorrect Request!'}), 400

# Facilitate updating of CCTV detection settings
@app.route('/UpdateCamConfig', methods=['POST'])
def update_cam_config():
    data = request.get_json()

    if not data or 'SerialNumber' not in data:
        return jsonify({'message': 'SerialNumber is required!'}), 400

    serial_number = data['SerialNumber']

    # Update the record with the given SerialNumber
    update_result = cctv_profiles.update_one(
        {"SerialNumber": serial_number},
        {"$set": data}
    )

    if update_result.matched_count == 0:
        return jsonify({'message': 'Camera with the given SerialNumber not found!'}), 404

    return jsonify({'message': 'Camera configuration updated successfully!'}), 200

# Endpoint to manage system setup
@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'GET':
        # Initialize alarm state if not set
        if alarmState.count_documents({}) == 0:
            document = {
                "ArmState": False,
                "TriggerState": False,
                "LastArm": '',
                "LastTrigg": '',
                "Timestamp": datetime.now()
            }
            alarmState.insert_one(document)
            fade_in_out('00ffe9', 2)

        print("GET setup called")

        # Insert default setup if none exists
        if setups.count_documents({}) == 0:
            new_setup = {
                "system_name": "example system",
                "location": {"latitude": 0.0, "longitude": 0.0},
                "sensors": 0,
                "passcode": 0000,
                "flag": "setup",
                "faces": {
                    "face1": {"name": "example-user", "img": "example-user.jpg"},
                    # Additional faces for recognition...
                }
            }
            setups.insert_one(new_setup)
            return jsonify(new_setup), 201
        else:
            # Return existing setup
            latest_record = setups.find_one(sort=[("created_at", DESCENDING)])
            print(latest_record)
            latest_record.pop('_id', None)
            latest_record.pop('passcode', None)
            return jsonify(latest_record), 200

    if request.method == 'POST':
        print("POST setup called")
        # Check if request is JSON
        if request.is_json:
            data = request.get_json()
            print(data)
            # Validate required fields
            required_fields = ["system_name", "location", "sensors", "passcode", "flag", "faces"]
            if not all(field in data for field in required_fields):
                return jsonify({"error": "Missing required fields"}), 400
            else:
                # Handle face images
                names = [entry["name"] for entry in data['faces']]
                if names:
                    print("Face names:", names)
                else:
                    print("Empty face list.")

                # Clean up face images directory
                directory_path = 'faces'
                valid_files = {f"{name}.png" for name in names}
                for filename in os.listdir(directory_path):
                    if filename not in valid_files:
                        file_path = os.path.join(directory_path, filename)
                        try:
                            os.remove(file_path)
                            print(f"Deleted: {file_path}")
                        except Exception as e:
                            print(f"Error deleting {file_path}: {e}")

                # Update setup record
                latest_record = setups.find_one(sort=[("created_at", DESCENDING)])
                if not latest_record:
                    return jsonify({"message": "No records found."}), 404

                record_id = latest_record['_id']
                result = setups.update_one({"_id": record_id}, {"$set": data})

                if result.matched_count == 0:
                    return jsonify({"message": "No setups found with the provided _id."}), 404
                else:
                    return jsonify({"message": "Setup updated successfully."}), 200

# Utility to check if passcode matches
def check_password(code, SystemCode):
    if len(code) != len(SystemCode):
        return False
    return all(code[i] == SystemCode[i] for i in range(len(code)))

# Endpoint to arm/disarm the system
@app.route('/setAlarm', methods=['POST'])
def set_alarm():
    data = request.get_json()
    authType = data.get('authType')
    authed_people = []
    latest_record = setups.find_one(sort=[("created_at", DESCENDING)])

    # Handle facial recognition authentication
    if authType == 'facial':
        faces = recognize()
        authed_faces = latest_record.get('faces')
        for face in authed_faces:
            authed_people.append(face['name'])

        # Check if recognized faces are authorized
        for detected_person in faces:
            if detected_person in authed_people:
                currentState = alarmState.find_one(sort=[("Timestamp", DESCENDING)])
                doc_id = currentState.get('_id')
                new_arm_state = not currentState['ArmState']
                TriggerState = not new_arm_state or currentState['TriggerState']
                current_time = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

                # Update alarm state
                update = {
                    "$set": {
                        "ArmState": new_arm_state,
                        "TriggerState": TriggerState,
                        "LastArm": current_time,
                        "Timestamp": current_time
                    }
                }
                result = alarmState.update_one({"_id": doc_id}, update)

                # Notify based on arm state
                if result.modified_count > 0:
                    print(new_arm_state)
                    fade_in_out('21a179', 1)
                    message = "Armed!" if new_arm_state else "Disarmed!"
                    create_security_notification(message, f"Alarm has been {message}", 3, current_time)
                return jsonify({"message": "Authed"}), 200
            else:
                return jsonify({"message": "Not allowed"}), 403

        return jsonify(faces), 200

    # Handle code-based authentication
    if authType == 'code':
        code = data.get('code')
        if code:
            SystemCode = latest_record.get('passcode')
            if check_password(code, SystemCode):
                currentState = alarmState.find_one(sort=[("Timestamp", DESCENDING)])
                doc_id = currentState.get('_id')
                new_arm_state = not currentState['ArmState']
                TriggerState = not new_arm_state or currentState['TriggerState']
                current_time = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

                # Update alarm state
                update = {
                    "$set": {
                        "ArmState": new_arm_state,
                        "TriggerState": TriggerState,
                        "LastArm": current_time,
                        "Timestamp": current_time
                    }
                }
                result = alarmState.update_one({"_id": doc_id}, update)
                if result.modified_count > 0:
                    print(new_arm_state)
                    fade_in_out('21a179', 1)
                    message = "Armed!" if new_arm_state else "Disarmed!"
                    create_security_notification(message, f"Alarm has been {message}", 3, current_time)
                return jsonify({"message": "Authed"}), 200
            else:
                return jsonify(code), 403
        else:
            return jsonify({"message", 'No code provided!'}), 400

# Endpoint for updating settings
@app.route('/updateSettings', methods=['POST'])
def updateSettingsReq():
    data = request.get_json()
    authType = data['authType']
    authed_people = []
    latest_record = setups.find_one(sort=[("created_at", DESCENDING)])

    # Handle facial recognition authentication
    if authType == 'facial':
        faces = recognize()
        authed_faces = latest_record.get('faces')
        for face in authed_faces:
            authed_people.append(face['name'])

        # Check if recognized faces are authorized
        for detected_person in faces:
            if detected_person in authed_people:
                data.pop('authType')
                data.pop('code')
                print("Authed")
                data = data['settings']

                # Validate required fields
                required_fields = ["system_name", "location", "sensors", "flag", "faces"]
                if not all(field in data for field in required_fields):
                    return jsonify({"error": "Missing required fields"}), 400

                # Handle face images and directory cleanup
                names = [entry["name"] for entry in data['faces']]
                directory_path = 'faces'
                valid_files = {f"{name}.png" for name in names}

                for filename in os.listdir(directory_path):
                    if filename not in valid_files:
                        file_path = os.path.join(directory_path, filename)
                        try:
                            os.remove(file_path)
                            print(f"Deleted: {file_path}")
                        except Exception as e:
                            print(f"Error deleting {file_path}: {e}")

                # Update setup record
                latest_record = setups.find_one(sort=[("created_at", DESCENDING)])
                if not latest_record:
                    return jsonify({"message": "No records found."}), 404

                record_id = latest_record['_id']
                result = setups.update_one({"_id": record_id}, {"$set": data})

                if result.matched_count == 0:
                    return jsonify({"message": "No setups found with the provided _id."}), 404
                else:
                    return jsonify({"message": "Setup updated successfully."}), 200
            else:
                return jsonify({"message": "Not allowed"}), 403
        
        return jsonify(faces), 200

    # Handle code-based authentication
    if authType == 'code':
        code = data.get('code')
        data = data.get("settings")
        if code:
            SystemCode = latest_record.get('passcode')

            if check_password(code, SystemCode):
                print("Authed")
                # Validate fields
                required_fields = ["system_name", "location", "sensors", "flag", "faces"]
                if not all(field in data for field in required_fields):
                    return jsonify({"error": "Missing required fields"}), 400
                
                # Handle face image and directory cleanup
                names = [entry["name"] for entry in data['faces']]
                directory_path = 'faces'
                valid_files = {f"{name}.png" for name in names}

                for filename in os.listdir(directory_path):
                    if filename not in valid_files:
                        file_path = os.path.join(directory_path, filename)
                        try:
                            os.remove(file_path)
                            print(f"Deleted: {file_path}")
                        except Exception as e:
                            print(f"Error deleting {file_path}: {e}")

                # Update setup record
                latest_record = setups.find_one(sort=[("created_at", DESCENDING)])
                if not latest_record:
                    return jsonify({"message": "No records found."}), 404

                record_id = latest_record['_id']
                result = setups.update_one({"_id": record_id}, {"$set": data})

                if result.matched_count == 0:
                    return jsonify({"message": "No setups found with the provided _id."}), 404
                else:
                    return jsonify({"message": "Setup updated successfully."}), 200
            else:
                return jsonify(code), 403
        else:
            return jsonify({"message": "No code provided!"}), 400

# Endpoint to register face via image capture
@app.route('/register_face', methods=['POST'])
def register_face():
    data = request.get_json()
    name = data.get('name')
    result = {}

    # Handle face registration in a separate thread
    def process_request():
        try:
            filepath = take_picture(name)
            if filepath:
                result['file_path'] = filepath
            else:
                result['error'] = "Failed to capture image"
        except Exception as e:
            result['error'] = str(e)

    thread = threading.Thread(target=process_request)
    thread.start()
    thread.join()

    # Return result or error
    if 'error' in result:
        return jsonify(result), 500
    else:
        return jsonify(result), 200

# Clear all security notifications
@app.route('/clear_security_notifications', methods=['POST'])
def clear_notifications():
    securityNotifications.drop()
    return jsonify({"message": "notifications cleared!"}), 200

# Retrieve latest sensor data
def get_sensors():
    pipeline = [
        {"$sort": {"SerialNumber": 1, "Timestamp": -1}},
        {
            "$group": {
                "_id": "$SerialNumber",
                "most_recent": {"$first": "$$ROOT"}
            }
        },
        {"$replaceRoot": {"newRoot": "$most_recent"}},
        {"$project": {
            "_id": 0,
            "SerialNumber": 1,
            "AlarmState": 1,
            "TamperState": 1,
            "Latitude": 1,
            "Longitude": 1,
            "Charge": 1,
            "SignalStrength": 1,
            "Timestamp": {"$dateToString": {"format": "%Y-%m-%dT%H:%M:%S.%LZ", "date": "$Timestamp"}}
        }}
    ]
    result = sensors.aggregate(pipeline)
    sensors_list = list(result)
    return sensors_list

def get_cctv():
    pipeline = [
        {"$sort": {"SerialNumber": 1, "Timestamp": -1}},
        {
            "$group": {
                "_id": "$SerialNumber",
                "most_recent": {"$first": "$$ROOT"}
            }
        },
        {"$replaceRoot": {"newRoot": "$most_recent"}},
        {"$project": {
            "_id": 0,
            "SerialNumber": 1,
            "Label": 1,
            "Latitude": 1,
            "Longitude": 1,
            "Charge": 1,
            "SignalStrength": 1,
            "Timestamp": {"$dateToString": {"format": "%Y-%m-%dT%H:%M:%S.%LZ", "date": "$Timestamp"}}
        }}
    ]
    result = cctv.aggregate(pipeline)
    cctv_list = list(result)

    return cctv_list

# Create a new security notification
def create_security_notification(title, message, level, timestamp):
    notification = {
        "title": title,
        "message": message,
        "level": level,
        "timestamp": timestamp
    }
    securityNotifications.insert_one(notification)

# Get all security notifications
def check_security_notifications():
    notifications = []
    for notification in securityNotifications.find().sort("timestamp", DESCENDING):
        notification.pop('_id', None)
        notifications.append(notification)
    return notifications

# Background task to monitor sensor data and emit via WebSocket
def handle_request_sensors():
    while True:
        sensorlistSend = get_sensors()
        socketio.emit('sensor_data', {'sensors': sensorlistSend})
        print("Checking sensors")
        cctvlistSend = get_cctv()
        socketio.emit('cctv_data', {'cameras': cctvlistSend})
        print("Checking cameras")
        time.sleep(5)



# Background task to send security notifications
def send_security_notifications():
    while True:
        notifications = check_security_notifications()
        socketio.emit('security_notification', {'message': notifications})
        print("Checking Sec Notifs")
        time.sleep(2)

# 2024-08-29T15:06:08.636Z


# Background task to monitor alarm state and trigger alerts
def check_alarm_state():
    while True:
        alarm = alarmState.find_one(sort=[("Timestamp", DESCENDING)])
        sensors = get_sensors()
        cctvs = get_cctv()
        current_time = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
        now = datetime.now()
        if alarm:
            if alarm.get('ArmState'):
                print("Armed")
                for cctv in cctvs:
                    last_d_time = datetime.strptime(cctv.get('Timestamp'), "%Y-%m-%dT%H:%M:%S.%fZ")
                    time_diff = abs(last_d_time - now)
                    print(time_diff.seconds)
                    if time_diff.seconds < 3611:
                        print("Alarm Triggered!")
                        update = {
                            "$set": {
                                "TriggerState": True,
                                "LastTrigg": current_time,
                                "Timestamp": current_time
                            }
                        }
                        doc_id = alarm.get('_id')
                        query = {"_id": doc_id}
                        alarmState.update_one(query, update)

                for sensor in sensors:
                    if sensor.get('AlarmState'):
                        print("Alarm Triggered!")
                        update = {
                            "$set": {
                                "TriggerState": True,
                                "LastTrigg": current_time,
                                "Timestamp": current_time
                            }
                        }
                        doc_id = alarm.get('_id')
                        query = {"_id": doc_id}
                        alarmState.update_one(query, update)
                        break
                    else:
                        print("No activity detected")
            
            else:
                current_time = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
                update = {
                    "$set": {
                        "TriggerState": False,
                        "Timestamp": current_time
                    }
                }
                doc_id = alarm.get('_id')
                query = {"_id": doc_id}
                alarmState.update_one(query, update)
                print("Disarmed")
        else:
                print("No alarm state!")    
        time.sleep(2)

# Background task to send alarm state via WebSocket
def send_alarm_state():
    while True:
        alarm = alarmState.find_one(sort=[("Timestamp", DESCENDING)])
        if alarm:
            alarm.pop('_id', None)
            socketio.emit('alarm_state', {'alarm': alarm})
            if alarm['TriggerState']:
                fade_in_out('ff0000', 0.5)
        else:
            print("No State!")
        time.sleep(1)

if __name__ == '__main__':
    os.makedirs('faces', exist_ok=True)
    socketio.start_background_task(send_security_notifications)
    socketio.start_background_task(handle_request_sensors)
    socketio.start_background_task(check_alarm_state)
    socketio.start_background_task(send_alarm_state)
    app.run(host="0.0.0.0", port=5000)
