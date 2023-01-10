#include <StateMachine.h>

#define SIZE 10 

const int Pin0 = 15;
const int Pin1 = 2;
const int Pin2 = 4;

int number_of_samples = 10;
unsigned short *values[3];
int i = 0;

bool measurement = false; //maybe volatile!!! or critical_ISR
bool measureNOW = false;
String text = "";
char EOM = '#';
volatile int interruptCounter;
hw_timer_t *timer0 = NULL;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;

StateMachine machine = StateMachine();

//i guess my understanding of the library is this:
//machine.run() runs the specified state
//first runs state function and later added transitions
State* Init = machine.addState(&_init);
State* Idle = machine.addState(&_idle);
State* Read = machine.addState(&_read);

void IRAM_ATTR onTimer(){
    portENTER_CRITICAL_ISR(&timerMux); 
    interruptCounter++;
    measureNOW=true;
    portEXIT_CRITICAL_ISR(&timerMux);
}

void _init() {
  //reading the amount of measurements to take
  //which sensors are chosen to read 
  machine.transitionTo(Idle);
  Serial.print("InitDone#");
}

void _idle() {
//  Serial.print("IdleDone#");
delay(10); //we can kinda relax in idle
}

void _read() {
//  Serial.print("READ#");
  if (measurement) {
    if (measureNOW) {
      readADC();
      portENTER_CRITICAL_ISR(&timerMux); 
      measureNOW = false;
      portEXIT_CRITICAL_ISR(&timerMux); 
    }
  } else {
    for (int i = 0; i < 3; i++)
      free(values[i]);
    text = "Idle"; //choose one
    machine.transitionTo(Idle); //choose one
  }
}

bool transitionInit_Idle() {
  return (text == "Idle");
}

bool transitionIdle_Init() {
  return text == "Init";
}

bool transitionIdle_Read() {
  if (text == "Read") {
    measurement = true;
    //get number of samples
    if (Serial.available() > 0) {
      String received = Serial.readStringUntil(EOM);
      number_of_samples = received.toInt();
    }

    for (int i = 0; i < 3; i++)
      values[i] = (unsigned short *)calloc(number_of_samples, sizeof(short));
    timerAlarmEnable(timer0);
    return true;
  } else 
    return false;
}

bool transitionRead_Idle() {
  return text == "Idle";
}


void setup() {
  timer0=timerBegin(0,80 ,true); 
  timerAttachInterrupt(timer0, &onTimer, true);
  timerAlarmWrite(timer0,1000, true);

//  Init->addTransition(&transitionInit_Init, Init);
  Init->addTransition(&transitionInit_Idle, Idle); //not needed
  Idle->addTransition(&transitionIdle_Init, Init);
  Idle->addTransition(&transitionIdle_Read, Read);
  Read->addTransition(&transitionRead_Idle, Idle);
  
//add the ADC setup

  Serial.begin(115200);
  Serial.setTimeout(100);
  delay(100); //delay after begin
  machine.transitionTo(Idle); //Because init initializes the reading settings (maybe rename to setup or smth)
}

void loop() {;
  if (Serial.available()) 
    text = Serial.readStringUntil(EOM);
  machine.run();
}


void readADC(){
  values[0][i] = analogRead(Pin0);
  values[1][i] = analogRead(Pin1);
  values[2][i] = analogRead(Pin2);
  i++;  
  
  if (i >= number_of_samples) {
    timerAlarmDisable(timer0);
    for (int k = 0; k < number_of_samples; k++) {
      for (int j = 0; j < 3; j++) {
        unsigned char buff[2];
        buff[0] = values[j][k] & 0xFF;
        buff[1] = (values[j][k] >> 8) & 0xFF;
          Serial.write(buff, 2);
          Serial.write("\r\n");
      }
    }
    i = 0;
    measurement = false; // or maybe machine.transitionTo(Idle);
  }
}
