#include "BluetoothSerial.h"

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif
BluetoothSerial SerialBT;

#define SIZE 10

const int Pin0 = 34;
const int Pin1 = 4;
const int Pin2 = 39;

short Value[SIZE][3];
int i = 0;

volatile int interruptCounter;
hw_timer_t *timer0 = NULL;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;

void IRAM_ATTR onTimer(){
    portENTER_CRITICAL_ISR(&timerMux);
    interruptCounter++;
    portEXIT_CRITICAL_ISR(&timerMux);
}


void setup() {
    Serial.begin(115200);

//    analogSetWidth(9);   
    
    timer0=timerBegin(0,80 ,true); //prescaler->mikrosekundy
    timerAttachInterrupt(timer0, &onTimer, true);
    timerAlarmWrite(timer0,1000, true);
    timerAlarmEnable(timer0);
    
    Serial.begin(115200);
    delay(100);
    SerialBT.begin("ESP32");
}

void loop() {

//  delay(10); 

  if(interruptCounter > 0){
      portENTER_CRITICAL(&timerMux);
      interruptCounter--;
      portEXIT_CRITICAL(&timerMux);
      readADC();
  }
}


void readADC(){
  if (i >= SIZE) {
    for (int j = 0; j < SIZE; j++) {
      for (int k = 0; k < 3; k++) {
        SerialBT.println(Value[j][k]);
      }  
    }
    i = 0;
  }
  Value[i][0] = analogRead(Pin0);
  Value[i][1] = analogRead(Pin1);
  Value[i][2] = analogRead(Pin2);
  i++;
}
