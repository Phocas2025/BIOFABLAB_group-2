/*void setup() {
  //pinMode(13, OUTPUT);
  delay(2000);

}

void loop() {
  //digitalWrite(13, HIGH);
}
*/

//void setup() {
  //pinMode(13, OUTPUT);
  //Serial.begin(9600);
//}

//void loop() {
  //digitalWrite(13, HIGH);
  //delay(500);
  //digitalWrite(13, LOW);
  //delay(500);
 // Serial.print("hi\n");
//}
// change this to fit the number of steps per revolution
// for your motor
 
// initialize the stepper library on pins 8 through 11:
#include <Stepper.h>
const int stepsPerRevolution = 300;  
Stepper myStepper(stepsPerRevolution, 8, 9, 10, 11);
  
void setup() {
  // set the speed at 60 rpm:
  myStepper.setSpeed(6);
  // initialize the serial port:
  Serial.begin(9600);
}
 
void loop() {
  // step one revolution  in one direction:
  Serial.println("clockwise");
  myStepper.step(stepsPerRevolution);
  delay(500);
 
  // step one revolution in the other direction:
  Serial.println("counterclockwise");
  myStepper.step(-stepsPerRevolution);
  delay(500);
}
/*#include <Stepper.h>   
#define STEPS 100  
Stepper stepper(STEPS, 8, 9, 10, 11);  
int previous = 0;  
void setup()
{
  stepper.setSpeed(90);
 }   
 void loop()
 {    
   int val = analogRead(0);      
   stepper.step(val - previous);     
   previous = val;
 } */