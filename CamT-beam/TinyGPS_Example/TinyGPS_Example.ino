#include "LoRaBoards.h"
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <LoRa.h>
#include <TinyGPS++.h>

TinyGPSPlus gps;

// This board is responsible for hosting a WiFi network that a
// Raspberry PI connects to and submits it's detected objects

const char* ssid = "CAM1";            
const char* password = "password123";  
const char* serial = "CN000001";

int batteryPercent = 0;

// Initialize the web server on port 80
WebServer server(80);

// Variable to track the last POST request time
unsigned long lastPostTime = 0;
const unsigned long postInterval = 3000; // 3 seconds in milliseconds

// Handle POST request to "/upload"
void handleUpload() {

  // Check if the last POST request was made within the last 3 seconds
  unsigned long currentTime = millis();
  if (currentTime - lastPostTime < postInterval) {
    Serial.println("Ignoring request, too soon since last request.");
    server.send(429, "application/json", "{\"error\":\"Too many requests, please wait\"}");
    return;
  }

  // Update the last post time
  lastPostTime = currentTime;

  // GPS Positioning code.
  float latitude = 0.0;
  float longitude = 0.0;
  if (gps.location.isValid()) {
    latitude = gps.location.lat();
    longitude = gps.location.lng();
    Serial.print(latitude, 6);
    Serial.print(F(","));
    Serial.print(longitude, 6);
  } else {
    Serial.print(F("INVALID"));
  }
  Serial.println(gps.satellites.value());

  // Verify data
  if (server.hasArg("plain") == false) {
    server.send(400, "application/json", "{\"error\":\"No data received\"}");
    return;
  }
  uint16_t batteryPercent = 0;

#ifdef HAS_PMU
  if (PMU) {
    batteryPercent = PMU->getBatteryPercent();
  }
#endif

  String body = server.arg("plain");  

  // Parse JSON data
  StaticJsonDocument<2048> jsonDoc; 
  DeserializationError error = deserializeJson(jsonDoc, body);
  Serial.println(body);

  if (error) {
    Serial.println("JSON Invalid");
    server.send(400, "application/json", "{\"error\":\"Failed to parse JSON\"}");
    return;
  }

  // "label" field from JSON
  const char* label = jsonDoc["label"];

  // Check if the fields exist
  if (label == nullptr) {
    server.send(400, "application/json", "{\"error\":\"Missing base64 or label field\"}");
    return;
  }

  // Print received data to the Serial Monitor
  Serial.println("Received POST request:");
  Serial.println(serial);
  Serial.println(label);
  Serial.println(latitude);
  Serial.println(longitude);
  Serial.println(batteryPercent);

  // LoRa Translation
  byte payload[256];
  int index = 0;

  index += serializeString(payload + index, serial);
  index += serializeString(payload + index, label);
  index += serializeFloat(payload + index, latitude);
  index += serializeFloat(payload + index, longitude);
  index += serializeInteger(payload + index, batteryPercent);

  Serial.print("Sending packet: ");
  LoRa.beginPacket();
  LoRa.write(payload, index);
  LoRa.endPacket(true);
  Serial.println("Done!");

  // Send a response to the client
  server.send(200, "application/json", "{\"status\":\"success\",\"message\":\"Data received\"}");
}

void setup() {
  // Start Serial Monitor
  Serial.begin(115200);
  setupBoards();
  delay(1000);

  // Begin GPS serial connection
  Serial1.begin(9600);  

  Serial.println("LoRa Sender");
  LoRa.setPins(RADIO_CS_PIN, RADIO_RST_PIN, RADIO_DIO0_PIN);
  if (!LoRa.begin(LoRa_frequency)) {
    Serial.println("Starting LoRa failed!");
    while (1)
      ;
  }
  Serial.println("LoRa initialized.");
  // Start the Wi-Fi access point
  WiFi.softAP(ssid, password);
  Serial.print("Access Point started. IP address: ");
  Serial.println(WiFi.softAPIP());

  // Define the POST route
  server.on("/upload", HTTP_POST, handleUpload);

  // Start the server
  server.begin();
  Serial.println("HTTP server started.");
}

void loop() {
  // Reading data from the GPS module
  while (Serial1.available() > 0) {  
    gps.encode(Serial1.read());   
  }

  // Handle incoming client requests
  server.handleClient();
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

int serializeBoolean(byte* buffer, bool value) {
  buffer[0] = value ? 1 : 0;
  return 1;
}

int serializeInteger(byte* buffer, int value) {
  memcpy(buffer, &value, sizeof(value));
  return sizeof(value);
}
