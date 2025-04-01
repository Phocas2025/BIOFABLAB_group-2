#include <HX711_ADC.h>
#include <AccelStepper.h>

#if defined(ESP8266) || defined(ESP32) || defined(AVR)
#include <EEPROM.h>
#endif

// Load Cell Pins
const int HX711_dout = 3; // HX711 data output pin
const int HX711_sck = 2;  // HX711 clock pin

// Stepper Motor Pins
#define IN1 8
#define IN2 9
#define IN3 10
#define IN4 11
#define HALFSTEP 4  // 4-step mode for 28BYJ-48 motor

// HX711 Load Cell Setup
HX711_ADC LoadCell(HX711_dout, HX711_sck);
const int calVal_eepromAdress = 0;
unsigned long t = 0;

// Stepper Motor Setup
AccelStepper stepper(HALFSTEP, IN1, IN2, IN3, IN4);

void setup() {
  Serial.begin(9600);
  delay(10);
  Serial.println("Initializing Load Cell and Stepper Motor...");

  // Load Cell Initialization
  LoadCell.begin();
  float calibrationValue = 45000.0; // Set calibration value
  LoadCell.setCalFactor(calibrationValue);
  unsigned long stabilizingTime = 2000; // Allow stabilization
  boolean _tare = true; // Tare at startup
  LoadCell.start(stabilizingTime, _tare);
  
  if (LoadCell.getTareTimeoutFlag()) {
    Serial.println("Load cell timeout! Check wiring.");
    while (1);
  } else {
    Serial.println("Load cell ready.");
  }

  // Stepper Motor Initialization
  stepper.setMaxSpeed(100.0);
  stepper.setAcceleration(50.0);
  Serial.println("Stepper motor ready.");
}

void loop() {
  static boolean newDataReady = false;
  const int serialPrintInterval = 500; // Slow down serial output

  // **Load Cell Data Handling**
  if (LoadCell.update()) newDataReady = true;
  if (newDataReady) {
    if (millis() > t + serialPrintInterval) {
      float forceValue = LoadCell.getData();
      Serial.print("Force: ");
      Serial.println(forceValue);
      newDataReady = false;
      t = millis();
    }
  }

  // **Stepper Motor Movement**
  if (stepper.distanceToGo() == 0) {
    static bool direction = true;
    Serial.println(direction ? "Moving forward" : "Moving backward");

    stepper.move(direction ? 10000 : -10000);  // Move in set direction
    direction = !direction;  // Toggle direction for next move
  }

  stepper.run();  // Non-blocking step execution

  // **Serial Command for Tare**
  if (Serial.available() > 0) {
    char inByte = Serial.read();
    if (inByte == 't') {
      Serial.println("Performing tare...");
      LoadCell.tareNoDelay();
    }
  }

  if (LoadCell.getTareStatus()) {
    Serial.println("Tare complete.");
  }
}
