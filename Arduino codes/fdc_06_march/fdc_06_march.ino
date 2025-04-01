#include <HX711_ADC.h>
#include <AccelStepper.h>

#if defined(ESP8266) || defined(ESP32) || defined(AVR)
#include <EEPROM.h>
#endif

// Load Cell Pin definitions
const int HX711_dout = 3; // HX711 data output pin
const int HX711_sck = 2;  // HX711 clock pin

// Stepper Motor Pin definitions
const int stepsPerRevolution = 2048;
#define IN1 8
#define IN2 9
#define IN3 10
#define IN4 11
AccelStepper myStepper(AccelStepper::HALF4WIRE, IN1, IN2, IN3, IN4);

// HX711 constructor
HX711_ADC LoadCell(HX711_dout, HX711_sck);
const int calVal_eepromAdress = 0;
unsigned long t = 0;

void setup() {
  Serial.begin(9600);
  delay(10);
  Serial.println("Starting...");

  // Load Cell Initialization
  LoadCell.begin();
  float calibrationValue = 45000.0; // Set calibration value
  LoadCell.setCalFactor(calibrationValue);
  unsigned long stabilizingTime = 5000; // Allow time for stabilization
  boolean _tare = true; // Ensure tare is performed at startup
  LoadCell.start(stabilizingTime, _tare);
  
  if (LoadCell.getTareTimeoutFlag()) {
    Serial.println("Timeout! Check wiring and pin configurations.");
    while (1);
  } else {
    Serial.println("Startup complete. Load cell tared.");
  }

  // Stepper Motor Initialization
  myStepper.setMaxSpeed(500.0);
  myStepper.setAcceleration(200.0);
}

void loop() {
  static boolean newDataReady = false;
  const int serialPrintInterval = 500; // Adjust to slow down serial prints

  // Continuously update force measurement
  if (LoadCell.update()) newDataReady = true;
  if (newDataReady && millis() > t + serialPrintInterval) {
    float forceValue = LoadCell.getData();
    Serial.print("Force measurement: ");
    Serial.println(forceValue);
    newDataReady = false;
    t = millis();
  }

  // Update stepper motor movement
  myStepper.run();

  // Listen for serial commands
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    
    if (input.equalsIgnoreCase("t")) {
      Serial.println("Performing tare...");
      LoadCell.tareNoDelay();
    } else if (input.equalsIgnoreCase("No")) {
      Serial.println("Exiting program...");
      return;  // End the function (stops execution)
    } else {
      float X = input.toFloat(); // Convert input to float
      Serial.print("Moving stepper for X = ");
      Serial.print(X);
      Serial.println(" mm");

      // Convert X (vertical displacement) to steps
      long totalSteps = (X * 2048) / 0.2556;
      myStepper.move(totalSteps);
    }
  }

  // Confirm tare operation completion
  if (LoadCell.getTareStatus()) {
    Serial.println("Tare complete.");
  }
}

