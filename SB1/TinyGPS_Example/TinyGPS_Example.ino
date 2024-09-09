#include "LoRaBoards.h"
#include <TinyGPS++.h>
#include <Wire.h>
#include <Preferences.h>
#include <U8g2lib.h>
#include <LoRa.h>

TinyGPSPlus gps;

// Pin definitions
#define ECHO_PIN 14
#define TRIG_PIN 13
#define VIBRATION_SENSOR_PIN 25
#define JOYSTICK_X_PIN 32
#define JOYSTICK_Y_PIN 35
#define JOYSTICK_SW_PIN 15

// Serial number hardcoded into each board
const char* serial = "SN000001";

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

int passcode[4] = { 0, 0, 0, 0 };  // Array to store the inputted passcode
int Cpasscode[4] = { 1, 0, 0, 0 };
int currentDigit = -1;
bool enteringPasscode = false;    // Determines wether to show password entry screen
bool showConfig = false;          // Used to show the margin adjustment screen
bool showConfigDistance = false;  // Used to show the distance calibration screen

void setup() {
  setupBoards();
  delay(1000);
  Serial.begin(115200);

  // Pin mode setup
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(JOYSTICK_SW_PIN, INPUT_PULLUP);
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

  // Load margin and distance threshold values from Preferences
  preferences.begin("settings", false);
  margin = preferences.getInt("margin", 4);                // Default to 4 if not set
  DISTANCE_THRESHOLD = preferences.getInt("distance", 0);  // Default to 0 if not set
  preferences.end();
}

void loop() {
  // Reading data from the GPS module
  while (Serial1.available() > 0) {  
    gps.encode(Serial1.read());   
  }
  int switchState = digitalRead(JOYSTICK_SW_PIN);
  if (switchState == LOW) {
    unsigned long currentTime = millis();
    if ((currentTime - lastDebounceTime) > debounceDelay) {
      lastDebounceTime = currentTime;
      if (showConfig == false && showConfigDistance == false) {
        enteringPasscode = true;
        if (enteringPasscode == true) {
          // Increment to next input digit
          currentDigit++;
        } else {
          enteringPasscode = !enteringPasscode;
        }
      } else if (showConfig == true) {
        showConfig = false;
        showConfigDistance = true;

      } else if (showConfigDistance == true) {
        showConfigDistance = false;
      }
    }
  }
  if (enteringPasscode == true) {
    displayPasscodeScreen();
    checkJoystick();
  }

  if (showConfig == true) {
    currentDigit = -1;
    displaySetupScreen();
    adjustMargin();
  }

  if (showConfig, enteringPasscode == false && showConfigDistance == true) {
    displayDistanceSetup();
    distanceSetup();
  }
  // Logic to show Passcode then proceed to the adjust screen
  if (enteringPasscode == false && showConfig == false && showConfigDistance == false) {

    handleSensorData();
  }
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

  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  int sensorValue = digitalRead(VIBRATION_SENSOR_PIN); 
  if (sensorValue == LOW) {
    tamperStatus = true;
    Serial.println("TAMPER!");
  } else {
    tamperStatus = false;
  }
  duration = pulseIn(ECHO_PIN, HIGH);
  distance = duration * 0.034 / 2;

  if (distance > DISTANCE_THRESHOLD + margin || distance < DISTANCE_THRESHOLD - margin || tamperStatus == true) {
    alarmTriggered = true;
    resetStartTime = 0;
    Serial.println("Alarm triggered!");
  }

  if (distance < DISTANCE_THRESHOLD + margin && distance > DISTANCE_THRESHOLD - margin || tamperStatus == false) {
    if (resetStartTime == 0) {
      resetStartTime = millis();
    } else if (millis() - resetStartTime >= RESET_DELAY) {
      alarmTriggered = false;
    }
  } else {
    resetStartTime = 0;
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
// here
void displayDistanceSetup() {
  u8g2->clearBuffer();
  u8g2->drawStr(0, 10, "Set Detection Distance:");
  u8g2->setCursor(0, 30);
  u8g2->print(DISTANCE_THRESHOLD);
  u8g2->print(" cm");
  u8g2->sendBuffer();
}

void displaySetupScreen() {
  u8g2->clearBuffer();
  u8g2->drawStr(0, 10, "Set Margin:");
  u8g2->setCursor(0, 30);
  u8g2->print(margin);
  u8g2->print(" cm");
  u8g2->sendBuffer();
}

// Distance setup function, allows for calibration of trigger distance.
void distanceSetup() {

  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  duration = pulseIn(ECHO_PIN, HIGH);
  DISTANCE_THRESHOLD = duration * 0.034 / 2;

  preferences.begin("settings", false);
  preferences.putInt("distance", DISTANCE_THRESHOLD);
  preferences.end();
}

void adjustMargin() {
  enteringPasscode = false;
  int yValue = analogRead(JOYSTICK_Y_PIN);
  Serial.println(yValue);
  if (yValue < 1000 && previousYValue >= 1000) {
    margin++;
    if (margin > 100) {
      margin = 100;
    }
    Serial.print("Margin increased to: ");
    Serial.println(margin);
  } else if (yValue > 4085 && previousYValue >= 2500) {
    margin--;
    if (margin < 0) {
      margin = 0;
    }
    Serial.print("Margin decreased to: ");
    Serial.println(margin);
  }

  previousYValue = yValue;

  preferences.begin("settings", false);
  preferences.putInt("margin", margin);
  preferences.end();
}

void displayPasscodeScreen() {
  showConfig = false;
  u8g2->clearBuffer();
  u8g2->drawStr(0, 10, "Enter Passcode:");

  for (int i = 0; i < 4; i++) {
    if (i < currentDigit) {
      u8g2->drawGlyph(12 * i, 30, '0' + passcode[i]);
    } else if (i == currentDigit) {
      u8g2->drawGlyph(12 * i, 30, '0' + passcode[i]);
    } else {
      u8g2->drawGlyph(12 * i, 30, '-');
    }
  }

  u8g2->sendBuffer();
}

void checkJoystick() {
  int correctCount = 0;
  int yValue = analogRead(JOYSTICK_Y_PIN);
  Serial.println(yValue);
  if (yValue < 1000 && previousYValue >= 1000) {
    passcode[currentDigit] = (passcode[currentDigit] + 1) % 10;
    if (passcode[currentDigit] > 9) {
      passcode[currentDigit] = 9;
    }

  } else if (yValue > 4085 && previousYValue >= 2500) {
    passcode[currentDigit] = (passcode[currentDigit] - 1) % 10;
    if (passcode[currentDigit] < 0) {
      passcode[currentDigit] = 0;
    }
  }
  Serial.print(currentDigit);
  if (currentDigit > 4) {
    currentDigit = 5;
    for (int i = 0; i < 4; i++) {
      if (passcode[i] == Cpasscode[i]) {
        correctCount++;
      } else {
        currentDigit = -1;
      }
    }
    Serial.print("Correct entries:");
    Serial.println(correctCount);


    if (correctCount == 4) {
      enteringPasscode = false;
      currentDigit = 0;
      showConfig = true;
      passcode[0] = 0;
      passcode[1] = 0;
      passcode[2] = 0;
      passcode[3] = 0;
    } else {
      enteringPasscode = false;
      showConfig = false;
      showConfigDistance = false;
      passcode[0] = 0;
      passcode[1] = 0;
      passcode[2] = 0;
      passcode[3] = 0;
    }
  }

  previousYValue = analogRead(JOYSTICK_Y_PIN);
}
