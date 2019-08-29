#include "WProgram.h"

extern "C" int main(void)
{
#ifdef USING_MAKEFILE

	// To use Teensy 3.0 without Arduino, simply put your code here.
	// For example:

	pinMode(13, OUTPUT);
	while (1) {
		int time = millis();
		digitalWrite(13, HIGH);
		delay((time/1000)%1000);
		time = millis();
		digitalWrite(13, LOW);
		delay((time/1000)%1000);
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

