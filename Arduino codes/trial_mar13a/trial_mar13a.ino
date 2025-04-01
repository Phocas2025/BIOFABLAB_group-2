#include <Stepper.h>  // If using a stepper motor
#include "HX711.h"    // Load cell amplifier

#define STEPS_PER_REV 200   // Adjust as per your stepper
#define MM_PER_STEP 0.02    // Adjust based on your setup

HX711 scale;
Stepper stepper(STEPS_PER_REV, 8, 9, 10, 11);

void setup() {
    Serial.begin(9600);
    scale.begin(A1, A0);  // Pins for the load cell
    scale.set_scale(2280.f); // Adjust this calibration factor
    scale.tare(); // Reset load cell

    stepper.setSpeed(10); // Set stepper speed (adjust as needed)
}

void loop() {
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        command.trim();

        if (command.startsWith("move")) {
            float distance = command.substring(5).toFloat();
            int steps = distance / MM_PER_STEP;

            for (int i = 0; i < abs(steps); i++) {
                stepper.step(steps > 0 ? 1 : -1);
                float force = scale.get_units();
                Serial.print("Displacement: ");
                Serial.print((i + 1) * MM_PER_STEP, 2);
                Serial.print(" mm | Force: ");
                Serial.print(force, 3);
                Serial.println(" N");
                delay(50);  // Adjust for smoother updates
            }
            Serial.println("DONE"); // Notify Python that motion is finished
        } 
        else if (command == "tare") {
            scale.tare();
            Serial.println("Load cell tared.");
        }
    }
}

