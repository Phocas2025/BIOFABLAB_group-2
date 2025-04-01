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
    Serial.begin(115200);
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

    // Stepper Motor Initialization (Reduced Speed)
    myStepper.setMaxSpeed(200.0);  // Reduced speed
    myStepper.setAcceleration(100.0); // Adjusted for smoother movement
}

void loop() {
    static boolean newDataReady = false;
    const int serialPrintInterval = 200; // Increased interval to 200 ms

    // Continuously update force measurement
    if (LoadCell.update()) newDataReady = true;
    if (newDataReady && millis() > t + serialPrintInterval) {
        float forceValue = LoadCell.getData();
        float displacement = myStepper.currentPosition() * mmPerStep; // Convert steps to mm
        
        Serial.print("Force: ");
        Serial.print(forceValue);
        Serial.print(" N, Displacement: ");
        Serial.print(displacement);
        Serial.println(" mm");
        
        newDataReady = false;
        t = millis();
    }

    // Run the stepper motor continuously, non-blocking
    myStepper.run(); 

    // Listen for serial commands
    if (Serial.available() > 0) {
        String input = Serial.readStringUntil('\n');
        input.trim();

        if (input.equalsIgnoreCase("t")) {
            Serial.println("Taring to zero...");
            LoadCell.tareNoDelay();  
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
            if (X == 0) {
                Serial.println("Error: Displacement cannot be zero.");
                return;
            }

            Serial.print("Moving stepper for X = ");
            Serial.print(X);
            Serial.println(" mm");

            long totalSteps = X / mmPerStep;

            // Move in the correct direction
            myStepper.move(totalSteps);
        }
    }

    // Ensure tare operation is completed
    if (LoadCell.getTareStatus()) {
        Serial.println("Tare complete.");
    }
}

