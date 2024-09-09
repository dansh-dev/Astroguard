#include "LoRaBoards.h"
#include <TinyGPS++.h>
#include <Wire.h>
#include <Preferences.h>
#include <U8g2lib.h>
#include <LoRa.h>

TinyGPSPlus gps;

// Pin definitions
#define VIBRATION_SENSOR_PIN 25
#define JOYSTICK_SW_PIN 15

// Serial number hardcoded into each board
const char* serial = "SN000002";

// Alarm status
boolean alarmTriggered = false;
boolean tamperStatus = false;


// Battery charge level
int charge = 0;
long duration;
long distance;  // This is the current distance
long DISTANCE_THRESHOLD = 0;

unsigned long resetStartTime = 0;
#define RESET_DELAY 5000

int margin = 2;
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 250;
int previousXValue = 0;
int previousYValue = 0;

Preferences preferences;

void setup() {
  setupBoards();
  delay(1000);
  Serial.begin(115200);

  pinMode(JOYSTICK_SW_PIN, INPUT);
  pinMode(VIBRATION_SENSOR_PIN, INPUT);
  
  // Begin GPS serial connection
  Serial1.begin(9600);  
  
  Serial.println("LoRa Sender");
  LoRa.setPins(RADIO_CS_PIN, RADIO_RST_PIN, RADIO_DIO0_PIN);
  if (!LoRa.begin(LoRa_frequency)) {
    Serial.println("Starting LoRa failed!");
    while (1)
      ;
  }
}

void loop() {
  // Reading data from the GPS module
  while (Serial1.available() > 0) {  
    gps.encode(Serial1.read());   
  }
  handleSensorData();
  delay(100); // Small delay to prevent overwhelming the serial monitor
  }

void handleSensorData() {
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
  boolean alarmState = alarmTriggered;
  Serial.println(alarmState);

  int sensorValue = digitalRead(VIBRATION_SENSOR_PIN); 
  if (sensorValue == LOW) {
    tamperStatus = true;
    alarmTriggered = true;
    Serial.println("TAMPER!");
  } else {
    tamperStatus = false;
  }
  // duration = pulseIn(ECHO_PIN, HIGH);
  // distance = duration * 0.034 / 2;

  int pirState = digitalRead(JOYSTICK_SW_PIN);
  if (pirState == HIGH) {
    Serial.println("Motion detected!"); // Print message to serial monitor
    alarmTriggered = true;
    resetStartTime = 0;
  } else {
     if (resetStartTime == 0) {
      resetStartTime = millis();
      if(tamperStatus == true ) {
        alarmTriggered = true;
      }
    } else if (millis() - resetStartTime >= RESET_DELAY) {
      alarmTriggered = false;
    }
    // digitalWrite(ledPin, LOW); // Turn off LED
    Serial.println("No motion detected!");
  }

  uint16_t batteryPercent = 0;

#ifdef HAS_PMU
  if (PMU) {
    batteryPercent = PMU->getBatteryPercent();
  }
#endif

  if (alarmTriggered != alarmState) {
    byte payload[256];
    int index = 0;

    index += serializeString(payload + index, serial);
    index += serializeBoolean(payload + index, alarmTriggered);
    index += serializeBoolean(payload + index, tamperStatus);
    index += serializeInteger(payload + index, batteryPercent);
    index += serializeFloat(payload + index, latitude);
    index += serializeFloat(payload + index, longitude);
    Serial.print("Sending packet: ");
    LoRa.beginPacket();
    LoRa.write(payload, index);
    LoRa.endPacket();
    delay(1000);
  }

#ifdef HAS_DISPLAY
String latitudeStr = String(latitude, 6); 
String longitudeStr = String(longitude, 6); 
  if (u8g2) {
    char buf[256];
    u8g2->clearBuffer();
    u8g2->drawStr(0, 12, "AstroGuard ");
    
    snprintf(buf, sizeof(buf), "Battery: %u%%", batteryPercent);
    u8g2->drawStr(0, 30, buf);
    u8g2->sendBuffer();
  }
#endif
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
