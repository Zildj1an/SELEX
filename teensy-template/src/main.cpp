#include "WProgram.h"

extern "C" int main(void)
{
#ifdef USING_MAKEFILE

	// To use Teensy 3.0 without Arduino, simply put your code here.
	// For example:


	float phase = 0.0;
	float twopi = 3.14159 * 2;
	elapsedMicros usec = 0;

  	analogWriteResolution(12);

	while(1) {
  	  float val = sin(phase) * 2000.0 + 2050.0;
  	  analogWrite(A14, (int)val);
  	  phase = phase + 0.02;
  	  if (phase >= twopi) phase = 0;
  	  while (usec < 500) ; // wait
  	  usec = usec - 500;
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

