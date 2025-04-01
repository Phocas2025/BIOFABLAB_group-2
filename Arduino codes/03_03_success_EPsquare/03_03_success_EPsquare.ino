/*#include <Stepper.h>

const int stepsPerRevolution = 2048;
Stepper myStepper(stepsPerRevolution, 8, 9, 10, 11);
const long totalSteps = 80000;  // Large step count
const long chunkSize = 10000;      // Run 10,000 steps at a time

void setup() {
  myStepper.setSpeed(8);
  long stepsRemaining = totalSteps;
  
  while (stepsRemaining > 0) {
    long stepsToMove = (stepsRemaining > chunkSize) ? chunkSize : stepsRemaining;
    myStepper.step(stepsToMove);
    stepsRemaining -= stepsToMove;
  }
}

void loop() {
  // Nothing needed here
}
*/
#include <Stepper.h>

const int stepsPerRevolution = 2048;
Stepper myStepper(stepsPerRevolution, 8, 9, 10, 11);
const long chunkSize = 10000;  // Run 10,000 steps at a time

void setup() {
  Serial.begin(9600);  // Initialize serial communication
  myStepper.setSpeed(8);
  
  while (true) {
    Serial.println("Enter vertical displacement (X in mm) or type 'No' to exit: ");
    
    while (!Serial.available());  // Wait for user input

    String input = Serial.readStringUntil('\n');  // Read user input
    input.trim();  // Remove whitespace
    
    if (input.equalsIgnoreCase("No")) {
      Serial.println("Exiting program...");
      return;  // End the function (stops execution)
    }
    
    float X = input.toFloat();  // Convert input to float
    Serial.print("Moving stepper for X = ");
    Serial.print(X);
    Serial.println(" mm");

    // Convert X (vertical displacement) to steps
    long totalSteps = (X * 2048) / 0.2556;
    bool moveBackward = (totalSteps < 0);  // Check direction
    long stepsRemaining = abs(totalSteps);

    while (stepsRemaining > 0) {
      long stepsToMove = (stepsRemaining > chunkSize) ? chunkSize : stepsRemaining;
      
      // Move forward or backward depending on X
      myStepper.step(moveBackward ? -stepsToMove : stepsToMove);
      
      stepsRemaining -= stepsToMove;
    }

    Serial.println("Movement complete.\n");
  }
}

void loop() {
  // Nothing needed here
}


