#ifndef PS_CURR_RANGE_H
#define PS_CURR_RANGE_H

#include <Arduino.h>
#include "ps_range.h"

namespace ps
{
    class CurrRange : public Range<uint16_t> 
    {
        public: 
            CurrRange() : Range<uint16_t>()  {};

            CurrRange(String name, float minValue, float maxValue, uint16_t maxInt)
                : Range<uint16_t>(name, minValue, maxValue, maxInt) {};
    
    };

} 

#endif
