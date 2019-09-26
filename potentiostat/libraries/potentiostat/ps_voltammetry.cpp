#include "ps_voltammetry.h"
#include "ps_time_utils.h"

namespace ps
{

    const String Voltammetry::TestKey("test");

    Voltammetry::Voltammetry()
    {
        availableTests_.push_back(&cyclicTest);
        availableTests_.push_back(&sinusoidTest);
        availableTests_.push_back(&constantTest);
        availableTests_.push_back(&squareWaveTest);
        availableTests_.push_back(&linearSweepTest);
    }
            

    BaseTest *Voltammetry::getTest(String name)
    {
        BaseTest *testPtr = nullptr;
        for (size_t i=0; i<availableTests_.size(); i++)
        {
            String currName = (availableTests_[i] -> getName()).trim();
            if (name.equals(currName))
            {
                testPtr = availableTests_[i];
                break;
            }
        }
        return testPtr;
    }

    
    ReturnStatus Voltammetry::getTest(JsonVariant &jsonMsg, JsonVariant &jsonDat, BaseTest* &testPtr)
    {
        ReturnStatus status;
        if (jsonMsg.containsKey(TestKey))
        {
            String testName = String((const char *)(jsonMsg[TestKey]));
            jsonDat[TestKey].set(jsonMsg[TestKey]);
            testPtr = getTest(testName);
            if (testPtr == nullptr)
            {
                status.success = false;
                status.message = String("test not found"); 
            }
        }
        else
        {
            status.success = false;
            status.message = String("json does not contain key: ") + TestKey;
        }
        return status;
    }


    ReturnStatus Voltammetry::getParam(JsonVariant &jsonMsg, JsonVariant &jsonDat)
    {
        ReturnStatus status;

        if (jsonMsg.containsKey(TestKey))
        {
            BaseTest *testPtr = nullptr;
            status = getTest(jsonMsg,jsonDat,testPtr);
            if (status.success && (testPtr != nullptr))
            {
                testPtr -> getParam(jsonDat);
            }
        }
        else
        {
            status.success = false;
            status.message = String("json does not contain key: ") + TestKey;
        }
        return status;
    }
    
    
    ReturnStatus Voltammetry::setParam(JsonVariant &jsonMsg, JsonVariant &jsonDat)
    {
        ReturnStatus status;

        if (jsonMsg.containsKey(TestKey))
        {
            BaseTest *testPtr = nullptr;
            status = getTest(jsonMsg,jsonDat,testPtr);
            if (status.success && (testPtr != nullptr))
            {
                status = testPtr -> setParam(jsonMsg,jsonDat);
            }
            else
            {
                status.success = false;
                status.message = String("test not found");
            }
        }
        else
        {
            status.success = false;
            status.message = TestKey + String(" key not found");
        }
        return status;
    } 
    
    
    ReturnStatus Voltammetry::getTestDoneTime(JsonVariant &jsonMsg, JsonVariant &jsonDat)
    {
        ReturnStatus status;

        if (!jsonMsg.containsKey(TestKey))
        {
            status.success = false;
            status.message = TestKey + String(" key not found");
            return status;
        }

        BaseTest *testPtr = nullptr;
        status = getTest(jsonMsg,jsonDat,testPtr);
        if ((!status.success) || (testPtr == nullptr))
        {
            status.success = false;
            status.message = String("test not found");
            return status;
        }

        String testName = testPtr -> getName();
        uint64_t doneTimeUs = testPtr -> getDoneTime();
        uint32_t doneTimeMs = convertUsToMs(doneTimeUs);

        jsonDat[TestKey].set(testName);
        jsonDat[TestDoneTimeKey].set(doneTimeMs);

        return status;
    }

    ReturnStatus Voltammetry::getTestNames(JsonVariant &jsonMsg, JsonVariant &jsonDat)
    {
        ReturnStatus status;
        JsonArray jsonNameArray = jsonDat.createNestedArray(TestNameArrayKey);
        for (size_t i=0; i<availableTests_.size(); i++)
        {
            jsonNameArray.add(availableTests_[i] -> getName());
        }
        return status;
    }


    ReturnStatus Voltammetry::getMuxTestNames(JsonVariant &jsonMsg, JsonVariant &jsonDat)
    {
        ReturnStatus status;
        JsonArray jsonNameArray = jsonDat.createNestedArray(TestNameArrayKey);
        for (size_t i=0; i<availableTests_.size(); i++)
        {
            if (availableTests_[i] -> isMuxCompatible())
            {
                jsonNameArray.add(availableTests_[i] -> getName());
            }
        }
        return status;
    }


    void Voltammetry::setSamplePeriod(uint64_t samplePeriod)
    {
        for (size_t i=0; i<availableTests_.size(); i++)
        {
            availableTests_[i] -> setSamplePeriod(samplePeriod);
        }
    }


} // namespace ps
