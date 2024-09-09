import unittest
from unittest.mock import patch, MagicMock
from flask import json
from datetime import datetime
import threading

# Bring in the necessary components from the Flask application
from app import app, sensors, setups, alarmState, cctv, cctv_profiles, securityNotifications

class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        # Initialize the Flask test client
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        # Clean up actions to be done after each test
        pass

    @patch('app.sensors.insert_one')
    @patch('app.setups.find_one')
    @patch('app.alarmState.find_one')
    @patch('app.create_security_notification')
    def test_input_data_valid_sn(self, mock_create_notification, mock_alarm_state, mock_setups_find, mock_sensors_insert):
        # Simulate the database responses for this test
        mock_setups_find.return_value = {
            'sensors': [{'serial': 'SN1234'}],
            'created_at': datetime.utcnow()
        }
        mock_alarm_state.return_value = {'ArmState': True}

        # Example of valid SN sensor data
        data = {
            "SerialNumber": "SN1234",
            "AlarmState": True,
            "TamperState": False,
            "Latitude": "51.5074",
            "Longitude": "0.1278",
            "Charge": 85,
            "SignalStrength": -70
        }
        response = self.app.post('/input_data', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 201)
        mock_sensors_insert.assert_called_once()
        mock_create_notification.assert_called_once_with(
            "Sensor Triggered!",
            "Sensor triggered:SN1234",
            4,
            unittest.mock.ANY  # Timestamp will vary
        )

    def test_input_data_missing_fields(self):
        # Test with required fields missing in the data
        data = {"SerialNumber": "SN1234"}
        response = self.app.post('/input_data', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Missing required fields", response.data)

    @patch('app.setups.find_one')
    def test_input_data_unrecognized_sensor(self, mock_setups_find):
        # Simulate a scenario where the sensor is not recognized
        mock_setups_find.return_value = {
            'sensors': [{'serial': 'SN9999'}],
            'created_at': datetime.utcnow()
        }

        data = {
            "SerialNumber": "SN1234",
            "AlarmState": True,
            "TamperState": False,
            "Latitude": "51.5074",
            "Longitude": "0.1278",
            "Charge": 85,
            "SignalStrength": -70
        }
        response = self.app.post('/input_data', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Sensor not recognized!", response.data)

    def test_input_data_non_json_request(self):
        # Test when the request content is not JSON
        response = self.app.post('/input_data', data="Not a JSON", content_type='text/plain')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Request must be JSON", response.data)

    @patch('app.cctv_profiles.find_one')
    @patch('app.setups.find_one')
    @patch('app.alarmState.find_one')
    @patch('app.cctv.insert_one')
    @patch('app.create_security_notification')
    def test_input_data_valid_cn_sensor_with_profile(self, mock_create_notification, mock_cctv_insert, mock_alarm_state, mock_setups_find, mock_profiles_find):
        # Simulate database responses for CN sensor with an existing profile
        mock_setups_find.return_value = {
            'sensors': [{'serial': 'CN5678'}],
            'created_at': datetime.utcnow()
        }
        mock_alarm_state.return_value = {'ArmState': True}
        mock_profiles_find.return_value = {
            "SerialNumber": "CN5678",
            "AllowedLabels": ["person", "cat"],
            "TimeStamp": datetime.utcnow()
        }

        data = {
            "SerialNumber": "CN5678",
            "Label": "person",
            "Latitude": "51.5074",
            "Longitude": "0.1278",
            "Charge": 85,
            "SignalStrength": -70
        }
        response = self.app.post('/input_data', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 201)
        mock_cctv_insert.assert_called_once()
        mock_create_notification.assert_called_once_with(
            "Camera Triggered!",
            "person detected!",
            3,
            unittest.mock.ANY
        )

    @patch('app.cctv_profiles.find_one')
    def test_get_cam_setup_success(self, mock_find_one):
        # Simulate successful retrieval of camera setup data
        mock_find_one.return_value = {
            "SerialNumber": "CN5678",
            "AllowedLabels": ["person", "cat"],
            "TimeStamp": datetime.utcnow(),
            "_id": "mock_id"
        }

        data = {"SerialNumber": "CN5678"}
        response = self.app.post('/getCamSetup', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data["SerialNumber"], "CN5678")
        self.assertNotIn("_id", response_data)

    def test_get_cam_setup_missing_serial_number(self):
        # Test when SerialNumber is missing in the request
        data = {}
        response = self.app.post('/getCamSetup', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"SerialNumber missing!", response.data)

    def test_get_cam_setup_incorrect_method(self):
        # Test with incorrect HTTP method (GET instead of POST)
        response = self.app.get('/getCamSetup')
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_update_cam_config_missing_serial_number(self):
        # Test when SerialNumber is missing in the configuration update
        data = {}
        response = self.app.post('/UpdateCamConfig', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"SerialNumber is required!", response.data)

    @patch('app.cctv_profiles.update_one')
    def test_update_cam_config_success(self, mock_update_one):
        # Simulate a successful camera configuration update
        mock_update_one.return_value.matched_count = 1
        data = {
            "SerialNumber": "CN5678",
            "AllowedLabels": ["person", "cat"]
        }
        response = self.app.post('/UpdateCamConfig', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Camera configuration updated successfully!", response.data)

    @patch('app.cctv_profiles.update_one')
    def test_update_cam_config_camera_not_found(self, mock_update_one):
        # Simulate a scenario where the camera is not found in the database
        mock_update_one.return_value.matched_count = 0
        data = {
            "SerialNumber": "CN5678",
            "AllowedLabels": ["person", "cat"]
        }
        response = self.app.post('/UpdateCamConfig', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Camera with the given SerialNumber not found!", response.data)

    @patch('app.alarmState.count_documents')
    @patch('app.setups.count_documents')
    @patch('app.setups.find_one')
    def test_setup_get_existing_setup(self, mock_setups_find, mock_setups_count, mock_alarm_count):
        # Simulate retrieval of an existing setup
        mock_alarm_count.return_value = 1
        mock_setups_count.return_value = 1
        mock_setups_find.return_value = {
            "system_name": "existing system",
            "location": {"latitude": 10.0, "longitude": 20.0},
            "sensors": 5,
            "passcode": 1234,
            "flag": "setup",
            "faces": {
                "face1": {"name": "user1", "img": "user1.jpg"}
            },
            "_id": "mock_id"
        }

        response = self.app.get('/setup')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data["system_name"], "existing system")
        self.assertNotIn("passcode", response_data)
        self.assertIn("faces", response_data)

    @patch('app.setups.find_one')
    @patch('app.setups.update_one')
    @patch('app.create_security_notification')
    @patch('app.os.listdir')
    @patch('app.os.remove')
    def test_setup_post_update_existing_setup(self, mock_os_remove, mock_os_listdir, mock_create_notification, mock_setups_update, mock_setups_find):
        # Simulate updating an existing setup with new information
        mock_setups_find.return_value = {
            "_id": "mock_id",
            "system_name": "existing system",
            "location": {"latitude": 10.0, "longitude": 20.0},
            "sensors": 5,
            "passcode": 1234,
            "flag": "setup",
            "faces": {
                "face1": {"name": "user1", "img": "user1.jpg"}
            },
            "created_at": datetime.utcnow()
        }
        mock_setups_update.return_value.matched_count = 1
        mock_os_listdir.return_value = ["user1.png", "user2.png"]

        # New setup data
        data = {
            "system_name": "updated system",
            "location": {"latitude": 30.0, "longitude": 40.0},
            "sensors": 10,
            "passcode": 5678,
            "flag": "setup",
            "faces": [
                {"name": "user2", "img": "user2.jpg"},
                {"name": "user3", "img": "user3.jpg"}
            ]
        }
        response = self.app.post('/setup', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        mock_setups_update.assert_called_once()
        # Ensure that old face images not included in the new setup are removed
        mock_os_remove.assert_called_with('faces/user1.png')

    def test_setup_post_missing_fields(self):
        # Test when required fields are missing in setup POST request
        data = {
            "system_name": "updated system",
            # Other required fields are missing
        }
        response = self.app.post('/setup', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Missing required fields", response.data)

    @patch('app.take_picture')
    def test_register_face_success(self, mock_take_picture):
        # Simulate successful registration of a face
        mock_take_picture.return_value = 'faces/example-user.png'

        data = {"name": "example-user"}
        response = self.app.post('/register_face', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('file_path', response_data)
        self.assertEqual(response_data['file_path'], 'faces/example-user.png')

    @patch('app.take_picture')
    def test_register_face_failure(self, mock_take_picture):
        # Simulate a failure in face registration
        mock_take_picture.side_effect = Exception("Camera error")

        data = {"name": "example-user"}
        response = self.app.post('/register_face', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], "Camera error")

    @patch('app.securityNotifications.drop')
    def test_clear_security_notifications(self, mock_drop):
        # Simulate successfully clearing security notifications
        response = self.app.post('/clear_security_notifications')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"notifications cleared!", response.data)
        mock_drop.assert_called_once()

if __name__ == '__main__':
    unittest.main()
