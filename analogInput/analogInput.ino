// Potentiometer is connected to GPIO 34 (Analog ADC1_CH6) 
const int potPin = 34;
const int potPin1 = 4;
const int potPin2 = 39;
// variable for storing the potentiometer value
int potValue = 0;
int potValue1 = 0;
int potValue2 = 0;

short tab[3];

volatile int interruptCounter;

hw_timer_t *timer0 = NULL;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;

void IRAM_ATTR onTimer()
{
    portENTER_CRITICAL_ISR(&timerMux);
    interruptCounter++;
    portEXIT_CRITICAL_ISR(&timerMux);
}


void setup() {
    Serial.begin(115200);

    analogSetWidth(9);

    timer0=timerBegin(0,80 ,true); //prescaler->mikrosekundy
    timerAttachInterrupt(timer0, &onTimer, true);
    timerAlarmWrite(timer0,1000, true);
    timerAlarmEnable(timer0);

  delay(100);
}

void loop() {

  delay(500); //don't know why it's here, leave it but not sure it's good idea

  if(interruptCounter > 0){
      portENTER_CRITICAL(&timerMux);
      interruptCounter--;
      portEXIT_CRITICAL(&timerMux);

      readADC();
  }
}



void readADC(){
  tab[0] = analogRead(potPin);
  tab[1] = analogRead(potPin1);
  tab[2] = analogRead(potPin2);
  for(int i = 0; i < 3; i++) {
    Serial.println(tab[i]);
  }
}
