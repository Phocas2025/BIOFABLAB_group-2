#include <HX711_ADC.h>
#include <AccelStepper.h>
#include <EEPROM.h>

// Load Cell Pin definitions
const int HX711_dout = 3;
const int HX711_sck = 2;

// Stepper Motor Pin definitions
const int stepsPerRevolution = 2048;
#define IN1 8
#define IN2 9
#define IN3 10
#define IN4 11
AccelStepper myStepper(AccelStepper::HALF4WIRE, IN1, IN2, IN3, IN4);

// HX711 Constructor
HX711_ADC LoadCell(HX711_dout, HX711_sck);
const int calVal_eepromAdress = 0;
unsigned long t = 0;
const float mmPerStep = 0.2556 / 2048;

void setup() {
    Serial.begin(9600);
    delay(10);
    Serial.println("Starting...");

    // Load Cell Initialization
    LoadCell.begin();
    float calibrationValue;
    EEPROM.get(calVal_eepromAdress, calibrationValue);
    
    if (isnan(calibrationValue) || calibrationValue <= 0) {
        calibrationValue = 45000.0; // Default value
        EEPROM.put(calVal_eepromAdress, calibrationValue);
    }
    LoadCell.setCalFactor(calibrationValue);

    LoadCell.start(5000, true); // 5s stabilization, perform tare
    if (LoadCell.getTareTimeoutFlag()) {
        Serial.println("Timeout! Check wiring and connections.");
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
    const int serialPrintInterval = 200; // Reduced interval for faster updates

    // Continuously update force measurement
    if (LoadCell.update()) newDataReady = true;
    if (newDataReady && millis() > t + serialPrintInterval) {
        float forceValue = LoadCell.getData();
        Serial.print("Force measurement: ");
        Serial.println(forceValue);
        newDataReady = false;
        t = millis();
    }

    // Run the stepper motor continuously, non-blocking
    myStepper.run(); // Keep motor running without blocking the loop()

    // Listen for serial commands
    if (Serial.available() > 0) {
        String input = Serial.readStringUntil('\n');
        input.trim();

        if (input.equalsIgnoreCase("t")) {
            // Perform tare (reset to 0)
            Serial.println("Taring to zero...");
            LoadCell.tare();  // Use the built-in tare function to reset to zero
            Serial.println("Tare complete, current weight set to zero.");
        } 
        else if (input.startsWith("cal ")) { // Calibration command
            float newCal = input.substring(4).toFloat();
            if (newCal > 0) {
                LoadCell.setCalFactor(newCal);
                EEPROM.put(calVal_eepromAdress, newCal);
                Serial.print("New calibration factor set: ");
                Serial.println(newCal);
            } else {
                Serial.println("Error: Invalid calibration factor.");
            }
        }
        else if (input.equalsIgnoreCase("No")) {
            Serial.println("Exiting program...");
            return;
        }
        else {
            float X = input.toFloat();
            if (X <= 0) {
                Serial.println("Error: Displacement must be positive.");
                return;
            }

            Serial.print("Moving stepper for X = ");
            Serial.print(X);
            Serial.println(" mm");

            long totalSteps = X / mmPerStep;
            myStepper.move(totalSteps);  // Start the movement, non-blocking

            // You don't need to block for the motor to finish moving here, the loop will keep running and allow continuous updates
        }
    }
}
