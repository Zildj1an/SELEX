#ifndef PS_VOLT_RANGE_H
#define PS_VOLT_RANGE_H

#include <Arduino.h>
#include "ps_range.h"

namespace ps
{
    class VoltRange : public Range<uint16_t> 
    {
        public: 
            VoltRange() : Range<uint16_t>()  {};

            VoltRange(String name, float minValue, float maxValue, uint16_t maxInt)
                : Range<uint16_t>(name, minValue, maxValue, maxInt) {};
    
    };

} 

#endif
