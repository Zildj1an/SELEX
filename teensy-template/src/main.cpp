#include "WProgram.h"
#include "potentiostat.h"

using namespace ps;

SystemState systemState;

/*
	int16_t adc_read(uint8_t mux) {
	  uint8_t low;

	  ADCSRA = (1<<ADEN) | ADC_PRESCALER;             // enable ADC
	  ADCSRB = (1<<ADHSM) | (mux & 0x20);             // high speed mode
	  ADMUX = aref | (mux & 0x1F);                    // configure mux input
	  ADCSRA = (1<<ADEN) | ADC_PRESCALER | (1<<ADSC); // start the conversion
 	  while (ADCSRA & (1<<ADSC)) ;                    // wait for result
	    low = ADCL;                                     // must read LSB first
	  return (ADCH << 8) | low;                       // must read MSB only once!
	}
*/

void timerCallback() {
    systemState.updateTestOnTimer();
}
/*
void serialEvent() {
    systemState.updateMessageData();
}*/

extern "C" int main(void)
{
#ifdef USING_MAKEFILE

	// To use Teensy 3.0 without Arduino, simply put your code here.
	// For example:

    Serial.begin(UsbSerialBaudrate);
    systemState.initialize();
    systemState.setTestTimerCallback(timerCallback);	
    //pinMode(A14, OUTPUT);
    //analogWriteResolution(12);
    //pinMode(A10, INPUT);
    //analogReadResolution(12);
    //analogWrite(A14, 2048);

    while(1) {
        systemState.processMessages();
        systemState.serviceDataBuffer();
        systemState.updateMessageData();
	//Serial.println(analogRead(A10));
        delay(10);
    }

/*
  	analogWriteResolution(12);
	analogReadResolution(10);
    analogReference(DEFAULT);

	Serial.begin(9600);

	pinMode(13, OUTPUT);
	pinMode(A10, INPUT);
    pinMode(A14, OUTPUT);
  	analogWrite(A14, 2000);


	while(1) {
	  digitalWrite(13,HIGH);
	  int rval = analogRead(A10);
	  Serial.println(rval);
	  delay(1000);
	  digitalWrite(13,LOW);
      delay(1000);
  	  analogWrite(A14, 1000);
	}
*/
#else
	// Arduino's main() function just calls setup() and loop()....
	setup();
	while (1) {
		loop();
		yield();
	}
#endif
}

