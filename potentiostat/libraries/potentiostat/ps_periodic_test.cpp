#include "ps_periodic_test.h"
#include "ps_time_utils.h"

namespace ps
{ 

    PeriodicTest::PeriodicTest() 
    { 
        updateShiftInUs();
        setName("period");
    }


    void PeriodicTest::setAmplitude(float amplitude)
    {
        amplitude_ = amplitude;
    }


    float PeriodicTest::getAmplitude() const
    {
        return amplitude_;
    }


    void PeriodicTest::setOffset(float offset)
    {
        offset_ = offset;
    }


    float PeriodicTest::getOffset() const
    {
        return offset_;
    }


    void PeriodicTest::setPeriod(uint64_t period)
    {
        period_ = period;
        updateShiftInUs();
    }


    uint64_t PeriodicTest::getPeriod() const
    {
        return period_;
    }


    void PeriodicTest::setShift(float shift)
    {
        shift_ = shift;
        updateShiftInUs();
    }


    float PeriodicTest::getShift() const
    {
        return shift_;
    }


    void PeriodicTest::setNumCycles(uint32_t numCycles)
    {
        numCycles_ = numCycles;
    }


    uint32_t PeriodicTest::getNumCycles() const
    {
        return numCycles_;
    }


    uint32_t PeriodicTest::getCycleCount(uint64_t t) const
    {
        if (t < quietTime_)
        {
            return 0;
        }
        else
        {
            return uint32_t((t-quietTime_)/period_);
        }
    }


    bool PeriodicTest::isDone(uint64_t t) const
    {
        bool done = false;
        uint32_t cycleCount = getCycleCount(t);
        if (cycleCount >= numCycles_)
        {
            done = true;
        }
        return done;
    }


    uint64_t PeriodicTest::getDoneTime() const 
    {
        return quietTime_ + numCycles_*period_;
    }


    float PeriodicTest::getValue(uint64_t t) const
    {
        return 0.0;
    }


    float PeriodicTest::getMaxValue() const
    {
        return offset_ + amplitude_;
    }


    float PeriodicTest::getMinValue() const
    {
        return offset_ - amplitude_;
    }


    void PeriodicTest::getParam(JsonVariant &jsonDat)
    {
        BaseTest::getParam(jsonDat);

        ReturnStatus status;
        JsonVariant jsonDatPrm = getParamJsonVariant(jsonDat,status);

        if (status.success)
        {
            jsonDatPrm[AmplitudeKey].set(amplitude_);
            jsonDatPrm[OffsetKey].set(offset_);
            jsonDatPrm[PeriodKey].set(convertUsToMs(period_));
            jsonDatPrm[NumCyclesKey].set(numCycles_);
            jsonDatPrm[ShiftKey].set(shift_);
        }
    }

    ReturnStatus PeriodicTest::setParam(JsonVariant &jsonMsg, JsonVariant &jsonDat)
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
        setAmplitudeFromJson(jsonMsgPrm,jsonDatPrm,status);
        setOffsetFromJson(jsonMsgPrm,jsonDatPrm,status);
        setPeriodFromJson(jsonMsgPrm,jsonDatPrm,status);
        setNumCyclesFromJson(jsonMsgPrm,jsonDatPrm,status);
        setShiftFromJson(jsonMsgPrm,jsonDatPrm,status);

        return status;
    }


    // Protected Methods
    // ------------------------------------------------------------------------
    
    void PeriodicTest::setAmplitudeFromJson(JsonVariant &jsonMsgPrm, JsonVariant &jsonDatPrm, ReturnStatus &status)
    {
        if (jsonMsgPrm.containsKey(AmplitudeKey))
        {
            if (jsonMsgPrm[AmplitudeKey].is<float>())
            {
                setAmplitude(jsonMsgPrm[AmplitudeKey].as<float>());
                jsonDatPrm[AmplitudeKey].set(getAmplitude());
            }
            else if (jsonMsgPrm[AmplitudeKey].is<long>()) 
            {
                setAmplitude(float(jsonMsgPrm[AmplitudeKey].as<long>()));
                jsonDatPrm[AmplitudeKey].set(getAmplitude());
            }
            else
            {
                status.success = false;
                String errorMsg = AmplitudeKey + String(" not a float");
                status.appendToMessage(errorMsg);
            }
        }
    }


    void PeriodicTest::setOffsetFromJson(JsonVariant &jsonMsgPrm, JsonVariant &jsonDatPrm, ReturnStatus &status)
    {
        if (jsonMsgPrm.containsKey(OffsetKey))
        {
            if (jsonMsgPrm[OffsetKey].is<float>())
            {
                setOffset(jsonMsgPrm[OffsetKey].as<float>());
                jsonDatPrm[OffsetKey].set(getOffset());
            }
            else if (jsonMsgPrm[OffsetKey].is<long>())
            {
                setOffset(float(jsonMsgPrm[OffsetKey].as<long>()));
                jsonDatPrm[OffsetKey].set(getOffset());
            }
            else
            {
                status.success = false;
                String errorMsg = OffsetKey + String(" not a float");
                status.appendToMessage(errorMsg);
            }
        }
    }


    void PeriodicTest::setPeriodFromJson(JsonVariant &jsonMsgPrm, JsonVariant &jsonDatPrm, ReturnStatus &status)
    {
        if (jsonMsgPrm.containsKey(PeriodKey))
        {
            if (jsonMsgPrm[PeriodKey].is<unsigned long>())
            {
                setPeriod(convertMsToUs(jsonMsgPrm[PeriodKey].as<unsigned long>()));
                jsonDatPrm[PeriodKey].set(convertUsToMs(getPeriod()));
            }
            else
            {
                status.success = false;
                String errorMsg = PeriodKey + String(" not uint32");
                status.appendToMessage(errorMsg);
            }
        }
    }


    void PeriodicTest::setNumCyclesFromJson(JsonVariant &jsonMsgPrm, JsonVariant &jsonDatPrm, ReturnStatus &status)
    {
        if (jsonMsgPrm.containsKey(NumCyclesKey))
        {
            if (jsonMsgPrm[NumCyclesKey].is<unsigned long>())
            {
                setNumCycles(jsonMsgPrm[NumCyclesKey].as<unsigned long>());
                jsonDatPrm[NumCyclesKey].set(getNumCycles());
            }
            else
            {
                status.success = false;
                String errorMsg = NumCyclesKey + String(" not uint32");
                status.appendToMessage(errorMsg);
            }
        }
    }


    void PeriodicTest::setShiftFromJson(JsonVariant &jsonMsgPrm, JsonVariant &jsonDatPrm, ReturnStatus &status)
    {
        if (jsonMsgPrm.containsKey(ShiftKey))
        {
            if (jsonMsgPrm[ShiftKey].is<float>() || jsonMsgPrm[ShiftKey].is<long>())
            {
                float shiftTmp = 0.0;
                if (jsonMsgPrm[ShiftKey].is<float>())
                { 
                    shiftTmp = jsonMsgPrm[ShiftKey].as<float>();
                }
                else
                { 
                    shiftTmp = float(jsonMsgPrm[ShiftKey].as<long>());
                }

                if ((shiftTmp >= 0.0) || (shiftTmp <= 1.0))
                {
                    setShift(shiftTmp);
                    jsonDatPrm[ShiftKey].set(getShift());
                }
                else
                {
                    status.success = false;
                    String errorMsg = ShiftKey + String(" out of range");
                    status.appendToMessage(errorMsg);
                }
            }
            else
            {
                status.success = false;
                String errorMsg = ShiftKey + String(" not a float");
                status.appendToMessage(errorMsg);
            }
        }
    }


    void PeriodicTest::updateShiftInUs()
    {
        shiftInUs_ = uint64_t(double(shift_)*period_);
    }

}
