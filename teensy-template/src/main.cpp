#include "WProgram.h"
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
extern "C" int main(void)
{
#ifdef USING_MAKEFILE

	// To use Teensy 3.0 without Arduino, simply put your code here.
	// For example:


	float phase = 0.0;
	float twopi = 3.14159 * 2;
	elapsedMicros usec = 0;

  	analogWriteResolution(12);
	analogReadResolution(10);
        analogReference(DEFAULT);

	Serial.begin(9600);

	pinMode(13, OUTPUT);
	pinMode(A10, INPUT);


	while(1) {
	  digitalWrite(13,HIGH);
	  int rval = analogRead(A10);
	  Serial.println(rval);
	  delay(1000);
	  digitalWrite(13,LOW);
          delay(1000);
  	  float val = sin(phase) * 2000.0 + 2050.0;
  	  analogWrite(A14, (int)val);
  	  phase = phase + twopi/4;
  	  if (phase >= twopi) phase = 0;
  	  while (usec < 500) ; // wait
  	  usec = usec - 501;
	}

#else
	// Arduino's main() function just calls setup() and loop()....
	setup();
	while (1) {
		loop();
		yield();
	}
#endif
}

