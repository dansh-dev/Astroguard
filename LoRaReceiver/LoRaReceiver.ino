#include <LoRa.h>
#include "boards.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// This board is responsible for translation between LoRa and
// JSON for backend processing.

// Raspberry PI wifi credentials (Placeholders)
const char* ssid = "AstroGuard";
const char* password = "12345678";

String serverUrl;

void setup() {
  // Initializes board interfaces
  initBoard();
  delay(1500);

  // Connects to the wifi network
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    // Waits until a connection to the command centre is achieved
    delay(1000);
    Serial.print(".");
  }
  // Print the local IP address
  Serial.println("WiFi connected.");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  // Gets the IP of the Raspberry PI
  Serial.print("Default Gateway: ");
  Serial.println(WiFi.gatewayIP());
  serverUrl = "http://" + WiFi.gatewayIP().toString();

  // Sets up LoRa
  Serial.println("LoRa Receiver");

  LoRa.setPins(RADIO_CS_PIN, RADIO_RST_PIN, RADIO_DIO0_PIN);
  if (!LoRa.begin(LoRa_frequency)) {
    Serial.println("Starting LoRa failed!");
    while (1)
      ;
  }
}

void loop() {
  // Upon recieveing a packet it tries to parse it
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    // If packet is valid, deserialize it
    byte payload[256];
    int index = 0;
    while (LoRa.available()) {
      payload[index++] = LoRa.read();
    }

    // Definition of vars for deserialization
    char serial[256];
    char label[72];
    bool alarmTriggered;
    bool tamperStatus;
    float latitude;
    float longitude;
    int batteryPercent;

    index = 0;
    // Deserialize serial number string
    index += deserializeString(payload + index, serial);
    StaticJsonDocument<256> jsonDoc;
    if (serial[0] =='C') {
      // Checks if recieved sensor is a camera node

      index += deserializeString(payload + index, label);
      latitude = deserializeFloat(payload + index);
      index += sizeof(float);  // Increment the index by the size of the float
      longitude = deserializeFloat(payload + index);
      index += sizeof(float);  // Increment the index by the size of the float
      index += deserializeInteger(payload + index, &batteryPercent);

      // Print received data
      Serial.print("Received Serial: ");
      Serial.println(serial);
      Serial.print("Received Label: ");
      Serial.println(label);
      Serial.print("Received Battery Percent: ");
      Serial.println(batteryPercent);
      Serial.println("Recieved Longitude:");
      Serial.print(longitude, 6);
      Serial.println("Recieved Latitude");
      Serial.print(latitude, 6);
      // print RSSI of packet
      Serial.print("' with RSSI ");
      Serial.println(LoRa.packetRssi());

      // Encodes the fields into the JSON format for sending over HTTP
      jsonDoc["SerialNumber"] = serial;
      jsonDoc["Label"] = label;
      jsonDoc["Latitude"] = latitude;
      jsonDoc["Longitude"] = longitude;
      jsonDoc["Charge"] = batteryPercent;
      jsonDoc["SignalStrength"] = LoRa.packetRssi();


    } else {
      // Deserialize boolean values
      index += deserializeBoolean(payload + index, &alarmTriggered);
      index += deserializeBoolean(payload + index, &tamperStatus);
      index += deserializeInteger(payload + index, &batteryPercent);
      latitude = deserializeFloat(payload + index);
      index += sizeof(float);  // Increment the index by the size of the float
      longitude = deserializeFloat(payload + index);
      index += sizeof(float);  // Increment the index by the size of the float

      // Print received data
      Serial.print("Received Serial: ");
      Serial.println(serial);
      Serial.print("Received Alarm Triggered: ");
      Serial.println(alarmTriggered ? "true" : "false");
      Serial.print("Received Tamper Status: ");
      Serial.println(tamperStatus ? "true" : "false");
      Serial.print("Received Battery Percent: ");
      Serial.println(batteryPercent);

      Serial.println("Recieved Longitude:");
      Serial.print(longitude, 6);

      Serial.println("Recieved Latitude");
      Serial.print(latitude, 6);
      // print RSSI of packet
      Serial.print("' with RSSI ");
      Serial.println(LoRa.packetRssi());

      jsonDoc["SerialNumber"] = serial;
      jsonDoc["AlarmState"] = alarmTriggered;
      jsonDoc["TamperState"] = tamperStatus;
      jsonDoc["Latitude"] = latitude;
      jsonDoc["Longitude"] = longitude;

      jsonDoc["Charge"] = batteryPercent;
      jsonDoc["SignalStrength"] = LoRa.packetRssi();
    }
    // Serialize JSON object to string
    String jsonString;
    serializeJson(jsonDoc, jsonString);

    // Send JSON data to the server
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(serverUrl + ":5000/input_data");
      http.addHeader("Content-Type", "application/json");

      int httpResponseCode = http.POST(jsonString);

      if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.println(httpResponseCode);
        Serial.println(response);
      } else {
        Serial.print("Error on sending POST: ");
        Serial.println(httpResponseCode);
      }

      http.end();
    } else {
      Serial.println("Error in WiFi connection");
    }
  }


#ifdef HAS_DISPLAY
  // Get battery voltage
  uint16_t batteryPercent = 0;
#ifdef HAS_PMU
  if (PMU) {
    batteryPercent = PMU->getBatteryPercent();
  }
#endif
  if (u8g2) {
    u8g2->clearBuffer();
    char buf[256];
    u8g2->drawStr(0, 12, "Received OK!");
    snprintf(buf, sizeof(buf), "RSSI:%i", LoRa.packetRssi());
    u8g2->drawStr(0, 40, buf);
    // Displays battery charge
    snprintf(buf, sizeof(buf), "Battery: %u%%", batteryPercent);
    u8g2->drawStr(0, 56, buf);
    u8g2->sendBuffer();
  }
#endif
}

// Methods for deserialization
int deserializeString(byte* buffer, char* str) {
  int length = strlen((char*)buffer);
  strcpy(str, (char*)buffer);
  return length + 1;
}

int deserializeBoolean(byte* buffer, bool* value) {
  *value = buffer[0] == 1;
  return 1;
}

int deserializeInteger(byte* buffer, int* value) {
  memcpy(value, buffer, sizeof(*value));
  return sizeof(*value);
}

float deserializeFloat(const byte* buffer) {
  float value;
  memcpy(&value, buffer, sizeof(value)); 
  return value;
}

int serializeFloat(byte* buffer, float value) {
  memcpy(buffer, &value, sizeof(value));
  return sizeof(value);
}

int serializeString(byte* buffer, const char* str) {
  int length = strlen(str);
  memcpy(buffer, str, length + 1);  
  return length + 1;
}
