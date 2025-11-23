#include <AccelStepper.h>

#define dirPin 5
#define stepPin 2
#define motorInterfaceType 1

AccelStepper stepper(motorInterfaceType, stepPin, dirPin);

void setup() {

// for geared:
  stepper.setMaxSpeed(50);
  stepper.setAcceleration(20);

// for direct: 

  //stepper.setMaxSpeed(500);
  //stepper.setAcceleration(200);

}

void loop() {
  int buttonState = digitalRead(12);
  if (buttonState == HIGH) {
    // Move the motor x steps clockwise(200*16=3200 steps is 1 rotation):
    // For full steps, with sync belt = 200 * 3 = 600 steps is 1 rotation
    // stepper.move(89); //=+- 10° (without belt)
    //stepper.move(8); //= +-5° per step
    stepper.move(4); //= +-5° per step
    stepper.runToPosition();
    delay(500);
  }
}
