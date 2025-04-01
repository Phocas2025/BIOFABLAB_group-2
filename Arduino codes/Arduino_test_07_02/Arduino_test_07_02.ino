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

#include <HX711_ADC.h>

// Define HX711 pins
#define DT 3
#define SCK 2

// Create HX711 object
HX711_ADC scale(DT, SCK);

void setup() {
    Serial.begin(115200);
    scale.begin();
    scale.setCalFactor(42700000.2085);  // Calibration factor (adjust this)
    Serial.println("HX711 Ready!");
}

void loop() {
    scale.update();  
    float force = scale.getData();  // Get calibrated force
    Serial.print("Force: ");
    Serial.print(force);
    Serial.println(" N");
    delay(500);
}
