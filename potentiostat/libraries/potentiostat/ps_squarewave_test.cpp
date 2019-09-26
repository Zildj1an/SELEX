#include "ps_squarewave_test.h"
#include "ps_time_utils.h"
#include "ps_constants.h"
#include <math.h>

namespace ps 
{
    // Public methods
    // --------------------------------------------------------------------------------------------
    SquareWaveTest::SquareWaveTest()
    { 
        setName("squareWave");
        setMuxCompatible(false);
        setSampleMethod(SampleCustom);
        updateDoneTime();
        updateMaxMinValues();
        updateStepSign();
    };

    void SquareWaveTest::setStartValue(float value)
    {
        startValue_ = value;
        updateDoneTime();
        updateMaxMinValues();
        updateStepSign();
    }


    float SquareWaveTest::getStartValue()
    {
        return startValue_;
    }


    void SquareWaveTest::setFinalValue(float value)
    {
        finalValue_ = value;
        updateDoneTime();
        updateMaxMinValues();
        updateStepSign();
    }


    float SquareWaveTest::getFinalValue()
    {
        return finalValue_;
    }


    void SquareWaveTest::setStepValue(float value)
    {
        stepValue_ = fabs(value);
        updateDoneTime();
    }


    float SquareWaveTest::getStepValue()
    {
        return stepValue_;
    }


    void SquareWaveTest::setAmplitude(float value)
    {
        amplitude_ = fabs(value);
    }


    float SquareWaveTest::getAmplitude()
    {
        return amplitude_;
    }


    void SquareWaveTest::setWindow(float value)
    {
        window_ = fabs(value);
        window_ = std::max((float)0.0, window_);
        window_ = std::min((float)1.0, window_);
        updateWindowLenUs();
    }


    float SquareWaveTest::getWindow()
    {
        return window_;
    }


    float SquareWaveTest::getMaxValue() const 
    {
        float maxValue = std::max(startValue_, finalValue_) + amplitude_;
        return std::max(maxValue, quietValue_);
    }


    float SquareWaveTest::getMinValue() const 
    {
        float minValue = std::min(startValue_, finalValue_) - amplitude_;
        return std::min(minValue, quietValue_);
    }


    void SquareWaveTest::setSamplePeriod(uint64_t samplePeriod)
    {
        BaseTest::setSamplePeriod(samplePeriod);
        halfSamplePeriod_ = samplePeriod >> 1;
        updateDoneTime();
        updateWindowLenUs();
    }

    bool SquareWaveTest::isDone(uint64_t t) const 
    {
        if (t >= doneTime_)
        {
            return true;
        }
        else
        {
            return false;
        }
    }


    uint64_t SquareWaveTest::getDoneTime() const
    {
        return doneTime_;

    }

    void SquareWaveTest::reset()
    {
        numForward_ = 0;
        numReverse_ = 0;
        currForward_ = 0.0;
        currReverse_ = 0.0;
        testCnt_ = 0;
        isFirst_ = true;
    }


    float SquareWaveTest::getValue(uint64_t t) const 
    {
        float value = 0.0;
        if ( t < quietTime_)
        {
            value = quietValue_;
        }
        else
        {
            uint64_t stepModPos = (t - quietTime_)%samplePeriod_;
            float stairValue = getStairValue(t);
	    /*Serial.print(stairValue);
	    Serial.print(' ');
            Serial.print(amplitude_);
	    Serial.print(' ');
            Serial.print((long)samplePeriod_);
	    Serial.print(' ');
            Serial.print((long)(t - quietTime_));
	    Serial.print(' ');
            Serial.print((long)stepModPos);
	    Serial.print(' ');
            Serial.println((long)halfSamplePeriod_);*/
            if (stepModPos < halfSamplePeriod_)
            {
                value = stairValue + amplitude_;
            }
            else
            {
                value = stairValue - amplitude_;
            }
	    //Serial.println(value);
        }
        return value;
    }


    float SquareWaveTest::getStairValue(uint64_t t) const
    {
        float stairValue = 0.0;
        if (t < quietTime_)
        {
            stairValue = quietValue_;
        }
        else
        {
            uint64_t tTest = t - quietTime_;
            uint64_t stepCount = tTest/samplePeriod_;
            stairValue = startValue_ + stepCount*stepSign_*stepValue_;
            stairValue = std::max(stairValue, minValue_);
            stairValue = std::min(stairValue, maxValue_);
        }
        return stairValue;
    }


    bool SquareWaveTest::updateSample(Sample sampleRaw, Sample &sampleTest) 
    {
        bool newSample = false;

        if (sampleRaw.t < quietTime_)
        {
            if ((testCnt_ > 0) && (testCnt_%sampleModulus_==0))
            {
                sampleTest.t = sampleRaw.t;
                sampleTest.volt = quietValue_;
                sampleTest.curr =  0.0;
                newSample = true;
            }
            testCnt_++;
        }
        else 
        {
            if (isFirst_)
            {
                isFirst_ = false;
                testCnt_ = 0;
            }

            uint64_t tTest = (sampleRaw.t - quietTime_);
            uint64_t stepModPos = tTest%samplePeriod_;

            if (stepModPos < halfSamplePeriod_)
            {
		//return true;
                // forward step
                if ((halfSamplePeriod_ - stepModPos - 1) < windowLenUs_)
                {
                    numForward_++;
                    currForward_ += sampleRaw.curr;
                }
            }
            else
            {
		//return false
                // reverse step
                if ((samplePeriod_ - stepModPos - 1) < windowLenUs_)
                {
                    numReverse_++;
                    currReverse_ += sampleRaw.curr;
                }
            }

            if ((testCnt_ > 0) && (testCnt_%sampleModulus_==0))
            {
                sampleTest.t = sampleRaw.t;
                sampleTest.volt = getStairValue(sampleRaw.t);
                sampleTest.curr = currForward_/numForward_ - currReverse_/numReverse_;
                numForward_ = 0;
                numReverse_ = 0;
                currForward_ = 0.0;
                currReverse_ = 0.0;
                newSample = true;
            }
            testCnt_++;
        }

        return newSample; 
    }


    void SquareWaveTest::getParam(JsonVariant &jsonDat)
    {
        BaseTest::getParam(jsonDat);

        ReturnStatus status;
        JsonVariant jsonDatPrm = getParamJsonVariant(jsonDat,status);

        if (status.success)
        {
            jsonDatPrm[StartValueKey].set(startValue_);
            jsonDatPrm[FinalValueKey].set(finalValue_);
            jsonDatPrm[StepValueKey].set(stepValue_);
            jsonDatPrm[AmplitudeKey].set(amplitude_);
            jsonDatPrm[WindowKey].set(window_);
        }
    }


    ReturnStatus SquareWaveTest::setParam(JsonVariant &jsonMsg, JsonVariant &jsonDat)
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
        setStepValueFromJson(jsonMsgPrm,jsonDatPrm,status);
        setAmplitudeFromJson(jsonMsgPrm,jsonDatPrm,status);
        setWindowFromJson(jsonMsgPrm,jsonDatPrm,status);
        return status;
    }

    // Protected methods
    // --------------------------------------------------------------------------------------------
   
    void SquareWaveTest::updateDoneTime()
    {
        if (stepValue_ > 0.0) 
        {
            uint64_t numSteps_ = uint64_t(ceil(fabs(finalValue_ - startValue_)/stepValue_))+1;
            uint64_t testDuration = numSteps_*uint64_t(samplePeriod_);
            doneTime_ = quietTime_ + testDuration;
        }
        else
        {
            doneTime_ = quietTime_;
        }
    }


    void SquareWaveTest::updateMaxMinValues()
    {
        maxValue_ = std::max(startValue_,finalValue_);
        minValue_ = std::min(startValue_,finalValue_);
    }


    void SquareWaveTest::updateWindowLenUs()
    {
        windowLenUs_ = uint64_t((halfSamplePeriod_- 1)*window_);
        windowLenUs_ = std::min(halfSamplePeriod_- 1, windowLenUs_);
        windowLenUs_ = std::max(uint64_t(1), windowLenUs_);
    }


    void SquareWaveTest::updateStepSign()
    {
        stepSign_ = (startValue_ <= finalValue_) ? 1.0 : -1.0;
    }


    void SquareWaveTest::setStartValueFromJson(JsonVariant &jsonMsgPrm, JsonVariant &jsonDatPrm, ReturnStatus &status)
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


    void SquareWaveTest::setFinalValueFromJson(JsonVariant &jsonMsgPrm, JsonVariant &jsonDatPrm, ReturnStatus &status)
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

    void SquareWaveTest::setStepValueFromJson(JsonVariant &jsonMsgPrm, JsonVariant &jsonDatPrm, ReturnStatus &status)
    {
        if (jsonMsgPrm.containsKey(StepValueKey))
        {
            if (jsonMsgPrm[StepValueKey].is<float>())
            {
                setStepValue(jsonMsgPrm[StepValueKey].as<float>());
                jsonDatPrm[StepValueKey].set(getStepValue());
            }
            else if (jsonMsgPrm[StepValueKey].is<long>())
            {
                setStepValue(float(jsonMsgPrm[StepValueKey].as<long>()));
                jsonDatPrm[StepValueKey].set(getStepValue());
            }
            else
            {
                status.success = false;
                String errorMsg = StepValueKey + String(" not a float");
                status.appendToMessage(errorMsg);
            }
        }
    }


    void SquareWaveTest::setAmplitudeFromJson(JsonVariant &jsonMsgPrm, JsonVariant &jsonDatPrm, ReturnStatus &status)
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

    void SquareWaveTest::setWindowFromJson(JsonVariant &jsonMsgPrm, JsonVariant &jsonDatPrm, ReturnStatus &status)
    {
        if (jsonMsgPrm.containsKey(WindowKey))
        {
            if (jsonMsgPrm[WindowKey].is<float>())
            {
                setWindow(jsonMsgPrm[WindowKey].as<float>());
                jsonDatPrm[WindowKey].set(getWindow());
            }
            else if (jsonMsgPrm[WindowKey].is<long>()) 
            {
                setWindow(float(jsonMsgPrm[WindowKey].as<long>()));
                jsonDatPrm[WindowKey].set(getWindow());
            }
            else
            {
                status.success = false;
                String errorMsg = WindowKey + String(" not a float");
                status.appendToMessage(errorMsg);
            }
        }
    }
 
} // namespace ps
