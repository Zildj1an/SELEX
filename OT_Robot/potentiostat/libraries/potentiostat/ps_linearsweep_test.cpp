#include "ps_linearsweep_test.h"
#include "ps_time_utils.h"
#include "ps_constants.h"

namespace ps
{

    LinearSweepTest::LinearSweepTest()
    { 
        setName("linearSweep");
        setMuxCompatible(true);
    }


    void LinearSweepTest::setStartValue(float value)
    {
        startValue_ = value;
    }


    float LinearSweepTest::getStartValue() const
    {
        return startValue_;
    }


    void LinearSweepTest::setFinalValue(float value)
    {
        finalValue_ = value;
    }


    float LinearSweepTest::getFinalValue() const
    {
        return finalValue_;
    }


    void LinearSweepTest::setDuration(uint64_t duration)
    {
        duration_ = duration;
    }


    uint64_t LinearSweepTest::getDuration() const
    {
        return duration_;
    }


    bool LinearSweepTest::isDone(uint64_t t) const 
    {
        if (t >= (duration_ + quietTime_))
        {
            return true;
        }
        else
        {
            return false;
        }
    }

    uint64_t LinearSweepTest::getDoneTime() const
    {
        return duration_ + quietTime_;
    }

    float LinearSweepTest::getValue(uint64_t t) const 
    {
        float value = 0.0;
        if (t < quietTime_)
        {
            value = quietValue_;
        }
        else
        {
            uint64_t s = t - quietTime_;
            value = ((finalValue_ - startValue_)*s)/duration_ + startValue_;
        }
        return value;
    }


    float LinearSweepTest::getMaxValue() const 
    {
        return std::max(startValue_, std::max(finalValue_, quietValue_));
    }


    float LinearSweepTest::getMinValue() const 
    {
        return std::min(startValue_, std::min(finalValue_, quietValue_));
    }


    void LinearSweepTest::getParam(JsonVariant &jsonDat)
    {
        BaseTest::getParam(jsonDat);

        ReturnStatus status;
        JsonVariant jsonDatPrm = getParamJsonVariant(jsonDat,status);

        if (status.success)
        {
            jsonDatPrm[StartValueKey].set(startValue_);
            jsonDatPrm[FinalValueKey].set(finalValue_);
            jsonDatPrm[DurationKey].set(convertUsToMs(duration_));
        }
    }

    ReturnStatus LinearSweepTest::setParam(JsonVariant &jsonMsg, JsonVariant &jsonDat)
    {
        ReturnStatus status;
        status = BaseTest::setParam(jsonMsg,jsonDat);

        // Extract parameter JsonVariants
        JsonVariant jsonMsgPrm = getParamJsonVariant(jsonMsg,status);
        if (!status.success)
        {
            return status;
        }

        JsonVariant jsonDatPrm = getParamJsonVariant(jsonDat,status);
        if (!status.success)
        {
            return status;
        }

        // Set parameters
        setStartValueFromJson(jsonMsgPrm,jsonDatPrm,status);
        setFinalValueFromJson(jsonMsgPrm,jsonDatPrm,status);
        setDurationFromJson(jsonMsgPrm,jsonDatPrm,status);

        return status;
    }

    // Protected methods
    // ----------------------------------------------------------------------------------

    void LinearSweepTest::setStartValueFromJson(JsonVariant &jsonMsgPrm, JsonVariant &jsonDatPrm, ReturnStatus &status)
    {
        if (jsonMsgPrm.containsKey(StartValueKey))
        {
            if (jsonMsgPrm[StartValueKey].is<float>())
            {
                setStartValue(jsonMsgPrm[StartValueKey].as<float>());
                jsonDatPrm[StartValueKey].set(getStartValue());
            }
            else if (jsonMsgPrm[StartValueKey].is<long>())
            {
                setStartValue(float(jsonMsgPrm[StartValueKey].as<long>()));
                jsonDatPrm[StartValueKey].set(getStartValue());
            }
            else
            {
                status.success = false;
                String errorMsg = StartValueKey + String(" not a float");
                status.appendToMessage(errorMsg);
            }
        }
    }


    void LinearSweepTest::setFinalValueFromJson(JsonVariant &jsonMsgPrm, JsonVariant &jsonDatPrm, ReturnStatus &status)
    {
        if (jsonMsgPrm.containsKey(FinalValueKey))
        {
            if (jsonMsgPrm[FinalValueKey].is<float>())
            {
                setFinalValue(jsonMsgPrm[FinalValueKey].as<float>());
                jsonDatPrm[FinalValueKey].set(getFinalValue());
            }
            else if (jsonMsgPrm[FinalValueKey].is<long>())
            {
                setFinalValue(float(jsonMsgPrm[FinalValueKey].as<long>()));
                jsonDatPrm[FinalValueKey].set(getFinalValue());
            }
            else
            {
                status.success = false;
                String errorMsg = FinalValueKey + String(" not a float");
                status.appendToMessage(errorMsg);
            }
        }
    }


    void LinearSweepTest::setDurationFromJson(JsonVariant &jsonMsgPrm, JsonVariant &jsonDatPrm, ReturnStatus &status)
    {
        if (jsonMsgPrm.containsKey(DurationKey))
        {
            if (jsonMsgPrm[DurationKey].is<unsigned long>())
            {
                setDuration(convertMsToUs(jsonMsgPrm[DurationKey].as<unsigned long>()));
                jsonDatPrm[DurationKey].set(convertUsToMs(getDuration()));
            }
            else
            {
                status.success = false;
                String errorMsg = DurationKey + String(" not uint32");
                status.appendToMessage(errorMsg);
            }
        }
    }


} // namespace ps
