#ifndef PS_RANGE_H
#define PS_RANGE_H

namespace ps
{

    template<typename IntType>
    class Range
    {
        public:

            Range() {};
            Range(String name, float minValue, float maxValue, IntType maxInt);
            String name() const;
            float minValue() const;
            float maxValue() const;
            IntType maxInt() const;
            inline IntType valueToInt(float volt) const;
            inline float intToValue(IntType value) const;

        private:

            String name_;
            float minValue_;
            float maxValue_;
            IntType maxInt_;

    };


    template<typename IntType>
    Range<IntType>::Range(String name, float minValue, float maxValue, IntType maxInt)
        : name_(name), minValue_(minValue), maxValue_(maxValue), maxInt_(maxInt)
    {}

    template<typename IntType>
    String Range<IntType>::name() const
    {
        return name_;
    }

    template<typename IntType>
    float Range<IntType>::minValue() const
    {
        return minValue_;
    }

    template<typename IntType>
    float Range<IntType>::maxValue() const
    {
        return maxValue_;
    }

    template<typename IntType>
    IntType Range<IntType>::maxInt() const
    {
        return maxInt_;
    }

    template<typename IntType>
    inline IntType Range<IntType>::valueToInt(float volt) const
    {
        IntType value = IntType(float(maxInt_)*(volt-minValue_)/(maxValue_ - minValue_));
        return constrain(value,0,maxInt_);
    }

    template<typename IntType>
    inline float Range<IntType>::intToValue(IntType value) const
    {
        return (float(value)/float(maxInt_))*(maxValue_ - minValue_);
    }

}

#endif
