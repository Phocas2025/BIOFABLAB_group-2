#include <AccelStepper.h>

// Define the stepper motor connection type
#define HALFSTEP 4  // 4-step mode works best with the 28BYJ-48 motor

// Define motor control pins (connected to ULN2003 driver)
#define IN1 8
#define IN2 9
#define IN3 10
#define IN4 11

// Create an AccelStepper object using 4-wire mode
AccelStepper stepper(HALFSTEP, IN1, IN2, IN3, IN4);

void setup() {
  Serial.begin(9600);

  // Set motor speed and acceleration (slower speed)
  stepper.setMaxSpeed(100.0);  // Maximum speed (steps per second)
  stepper.setAcceleration(50.0);  // Acceleration (steps per second^2)
}

void loop() {
  // Clockwise movement
  Serial.println("Moving 20 steps clockwise");
  stepper.move(10000);  // Move 20 steps forward (clockwise)
  while (stepper.distanceToGo() != 0) {
    stepper.run();  // Moves the stepper until the target position is reached
  }
  delay(2000);  // Wait for 2 seconds before reversing

  // Counterclockwise movement
  Serial.println("Moving 20 steps counterclockwise");
  stepper.move(-10000);  // Move 20 steps backward (counterclockwise)
  while (stepper.distanceToGo() != 0) {
    stepper.run();  // Moves the stepper until the target position is reached
  }
  delay(2000);  // Wait for 2 seconds before repeating
}
