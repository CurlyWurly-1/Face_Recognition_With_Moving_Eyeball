#include <Servo.h>

Servo servo_tilt;  // create servo object to control a servo
Servo servo_pan;  // create servo object to control a servo


#define numOfValsRec 2
#define digitsPerValRec 3

int valsRec[numOfValsRec];
int stringLength = ( numOfValsRec * digitsPerValRec ) + 1 ;
int counter = 0;
bool triggered = false;
bool data_ready = false;
String receivedString;

void setup() {
  Serial.begin(9600);
  delay(100);
  servo_tilt.attach(9);  // attaches the servo on pin 9 to the servo object
  servo_pan.attach(10);  // attaches the servo on pin 9 to the servo object
  delay(100);
// Set initial "middle" Position
  servo_pan.write(79);                  // sets the servo position according to the scaled value
  servo_tilt.write(83);  
}

void receiveData() {
  while (Serial.available()&& !data_ready) {
    char c = Serial.read();
    if ( c== '#') {
      triggered = true;  
    }
    if (triggered){
      if (counter < stringLength){
        receivedString = String(receivedString+c);
        counter++;
      }
      if (counter >= stringLength) {
        data_ready = true;
        for (int i = 0; i< numOfValsRec; i++) {
          int num = (i * digitsPerValRec) + 1;
          valsRec[i] = receivedString.substring(num, num + digitsPerValRec).toInt();   
        }  
        receivedString = "";
        counter = 0;
        triggered = false;
      }
    }
  }
}

void loop() {
  receiveData();
  if (data_ready) {
    data_ready = false;
    servo_pan.write(valsRec[0]);                  // sets the servo position according to the scaled value
    servo_tilt.write(valsRec[1]);                  // sets the servo position according to the scaled value
  }
}
