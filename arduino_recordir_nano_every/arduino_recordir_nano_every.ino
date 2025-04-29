/*
Author: Flair
Revision: 1.2

Connections:
IR Receiver      Arduino
V+           ->  GPIO4
GND          ->  GPIO3
Signal Out   ->  GPIO2
*/


// ====================================================================
// Timer Defines
#ifdef ARDUINO_ARCH_MEGAAVR
#include "EveryTimerB.h"
#define Timer1 TimerB2 // use TimerB2 as a drop in replacement for Timer1
#else // assume architecture supported by TimerOne ....
#include "TimerOne.h"
#endif


// ====================================================================
// Program Defines
#define LEDPIN 13
#define maxLen 1500
#define SENSOR_5V 4
#define SENSOR_GND 3
#define SENSOR_OUT 2


// ====================================================================
// Program Buffer
volatile unsigned int irBuffer[maxLen]; //stores timings - volatile because changed by ISR
volatile unsigned int x = 0; //Pointer thru irBuffer - volatile because changed by ISR


// ====================================================================
// Program Functions
void gpioInit() {
  pinMode(SENSOR_5V, OUTPUT);
  pinMode(SENSOR_GND, OUTPUT);
  pinMode(SENSOR_OUT, INPUT);
  digitalWrite(SENSOR_5V, HIGH);
  digitalWrite(SENSOR_GND, LOW);
}

void setup() {
  Serial.begin(115200);
  while (!Serial);

  gpioInit();
  
  Timer1.initialize();
  Timer1.attachInterrupt(TimerHandler);
  Timer1.setPeriod(1000000); // like the TimerOne library this will start the timer as well, in microsecond resolution

  attachInterrupt(digitalPinToInterrupt(SENSOR_OUT), rxIR_Interrupt_Handler, CHANGE); // interrupt on GPIO toggle
}

void loop() {
  // This program is interrupt driven, as it should be.
}

void TimerHandler() {
  if (x) {
    detachInterrupt(digitalPinToInterrupt(SENSOR_OUT));//stop interrupts & capture until finshed here
    digitalWrite(LEDPIN, HIGH);//visual indicator that signal received
    Serial.print(F("Raw: (")); //dump raw header format - for library
    Serial.print((x - 1));
    Serial.print(F(") "));
    
    unsigned int local_max;
    local_max = 0;
    for (int i = 1; i < x; i++) {
      if (!(i & 0x1)) Serial.print(F("-"));
      Serial.print(irBuffer[i] - irBuffer[i - 1]);
      Serial.print(F(", "));
      if ((irBuffer[i] - irBuffer[i - 1]) > local_max) {
        local_max = irBuffer[i] - irBuffer[i - 1];
      }
    }
    x = 0;
    Serial.println();
    digitalWrite(LEDPIN, LOW);//end of visual indicator, for this time

    Timer1.stop();
    attachInterrupt(digitalPinToInterrupt(SENSOR_OUT), rxIR_Interrupt_Handler, CHANGE);//re-enable ISR for receiving IR signal
  }
  else {
    Serial.println();
  }
}

void rxIR_Interrupt_Handler() {
  if (x > (maxLen - 2)) {
    detachInterrupt(digitalPinToInterrupt(SENSOR_OUT));//stop interrupts
    Serial.println(F("Overflow! Exiting..."));
  }
  else {
    irBuffer[x] = micros(); //just continually record the time-stamp of signal transitions
    x++;
    Timer1.attachInterrupt(TimerHandler);
    Timer1.setPeriod(1000000); // like the TimerOne library this will start the timer as well
  }
}
