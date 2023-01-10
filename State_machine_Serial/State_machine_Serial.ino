#define SIZE 10 
#define MESURE_NUMBERS 2000 

const int Pin0 = 15;
const int Pin1 = 2;
const int Pin2 = 4;

short Value[SIZE][3];
int i = 0;

bool measurement = false;
bool measureNOW = false;
String text = "";

volatile int interruptCounter;
hw_timer_t *timer0 = NULL;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;

void IRAM_ATTR onTimer(){
    portENTER_CRITICAL_ISR(&timerMux); 
    interruptCounter++;
    measureNOW=true;
    portEXIT_CRITICAL_ISR(&timerMux);
}

void setup() {
    timer0=timerBegin(0,80 ,true); 
    timerAttachInterrupt(timer0, &onTimer, true);
    timerAlarmWrite(timer0,1000, true);
        
    delay(100);
    Serial.begin(115200);
}

void loop() {
  if (Serial.available() > 0) {
    text = Serial.readStringUntil('\n');

    if(text == "start") {
      timerAlarmEnable(timer0); 
      measurement = true;
    }
  }

//  if(interruptCounter > MESURE_NUMBERS) {
  if(text == "stop") {
    timerAlarmDisable(timer0);
    interruptCounter = 0;
    measurement = false;
  }

  if(measurement){
    if(measureNOW){
      readADC();
      measureNOW = false;
    }
  }

}

void readADC(){
  if (i >= SIZE) {
    for (int j = 0; j < SIZE; j++) {
      for (int k = 0; k < 3; k++) {
        Serial.println(Value[j][k]);
      }  
    }
    i = 0;
  }
  Value[i][0] = analogRead(Pin0);
  Value[i][1] = analogRead(Pin1);
  Value[i][2] = analogRead(Pin2);
  i++;
}
