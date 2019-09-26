#include "ps_system_state.h"
#include "util/atomic.h"


namespace ps
{

    SystemState::SystemState()
    { 
        testInProgress_ = false;
        lastSampleFlag_ = false;
        timerCnt_ = 0;
        test_ = nullptr;

        //currLowPass_.setParam(CurrLowPassParam);
        /*for (int i=0; i<NumMuxChan; i++)
        {
            currLowPass_.push_back(LowPass(CurrLowPassParam));
        }*/
        setSamplePeriod(DefaultSamplePeriod);
    }


    void SystemState::initialize()
    {

        delay(1000);
        StaticJsonDocument<100> doc;
        doc["initialize"] = "true";
        char output[100];
        serializeJson(doc, output);
        Serial.println(output);

        commandTable_.setClient(this);
        commandTable_.registerMethod(CommandKey,   RunTestCmd,            &SystemState::onCommandRunTest);
        commandTable_.registerMethod(CommandKey,   StopTestCmd,           &SystemState::onCommandStopTest);
        commandTable_.registerMethod(CommandKey,   SetParamCmd,           &SystemState::onCommandSetTestParam);
        commandTable_.registerMethod(CommandKey,   GetParamCmd,           &SystemState::onCommandGetTestParam);
        commandTable_.registerMethod(CommandKey,   SetSamplePeriodCmd,    &SystemState::onCommandSetSamplePeriod);
        commandTable_.registerMethod(CommandKey,   GetSamplePeriodCmd,    &SystemState::onCommandGetSamplePeriod);
        commandTable_.registerMethod(CommandKey,   GetTestDoneTimeCmd,    &SystemState::onCommandGetTestDoneTime);
        commandTable_.registerMethod(CommandKey,   GetTestNamesCmd,       &SystemState::onCommandGetTestNames);

        analogSubsystem_.initialize();
        analogSubsystem_.setVolt(0);
        messageReceiver_.reset();
    }


    ReturnStatus SystemState::onCommandRunTest(JsonVariant &jsonMsg, JsonVariant &jsonDat)
    {
        ReturnStatus status = voltammetry_.getTest(jsonMsg,jsonDat,test_);
        if (!status.success)
        {
            return status;
        }

        if (test_ == nullptr)
        {
            status.success = false;
            status.message = String("something is wrong, test_ == nullptr");
            return status;
        }

        startTest();
        return status;
    }


    ReturnStatus SystemState::onCommandStopTest(JsonVariant &jsonMsg, JsonVariant &jsonDat)
    {
        ReturnStatus status;
        stopTest();
        return status;
    }


    ReturnStatus SystemState::onCommandSetTestParam(JsonVariant &jsonMsg, JsonVariant &jsonDat)
    {
        ReturnStatus status = voltammetry_.setParam(jsonMsg,jsonDat);
        return status;
    }


    ReturnStatus SystemState::onCommandGetTestParam(JsonVariant &jsonMsg, JsonVariant &jsonDat)
    {
        ReturnStatus status = voltammetry_.getParam(jsonMsg,jsonDat);
        return status;
    }


    ReturnStatus SystemState::onCommandSetSamplePeriod(JsonVariant &jsonMsg, JsonVariant &jsonDat)
    {
        ReturnStatus status;
        if (!jsonMsg.containsKey(SamplePeriodKey))
        {
            status.success = false;
            status.message = String("json does not contain key: ") + SamplePeriodKey;
        }
        else
        {
            if (!jsonMsg[SamplePeriodKey].is<uint32_t>())
            {
                status.success = false;
                status.message = String("json ") + SamplePeriodKey + String(" value is not uin32_t");
            }
            else
            {
                uint32_t samplePeriodMs = jsonMsg[SamplePeriodKey].as<uint32_t>();
                uint32_t samplePeriodUs = uint32_t(convertMsToUs(samplePeriodMs));
                if (samplePeriodUs > MaximumSamplePeriod)
                {
                    status.success = false;
                    status.message = String("json ") + SamplePeriodKey + String(" value is too large");
                }
                else if (samplePeriodUs < MinimumSamplePeriod)
                {
                    status.success = false;
                    status.message = String("json ") + SamplePeriodKey + String(" value is too small");
                }
                else
                {
                    setSamplePeriod(samplePeriodUs);
                    jsonDat[SamplePeriodKey].set(convertUsToMs(getSamplePeriod()));
                }
            }
        }
        return status;
    }


    ReturnStatus SystemState::onCommandGetSamplePeriod(JsonVariant &jsonMsg, JsonVariant &jsonDat)
    {
        ReturnStatus status;
        jsonDat[SamplePeriodKey].set(convertUsToMs(getSamplePeriod()));
        return status;
    }

    
    ReturnStatus SystemState::onCommandGetTestDoneTime(JsonVariant &jsonMsg, JsonVariant &jsonDat)
    {
        ReturnStatus status;
        status = voltammetry_.getTestDoneTime(jsonMsg, jsonDat);
        return status;
    }

    ReturnStatus SystemState::onCommandGetTestNames(JsonVariant &jsonMsg, JsonVariant &jsonDat)
    {
        ReturnStatus status;
        status = voltammetry_.getTestNames(jsonMsg, jsonDat);
        return status;
    }

    void SystemState::updateMessageData()
    {
        messageReceiver_.readData();
    }


    void SystemState::processMessages()
    {

        if (messageReceiver_.available())
        {
            
            ReturnStatus status;
            StaticJsonDocument<JsonMessageBufferSize> messageJsonDocument;
            StaticJsonDocument<JsonMessageBufferSize> commandRespJsonDocument;

            String message = messageReceiver_.next();
            DeserializationError err = messageParser_.parse(message,messageJsonDocument);
            JsonVariant jsonMsg = messageJsonDocument.as<JsonVariant>(); 

            JsonVariant jsonDat = commandRespJsonDocument.createNestedObject();
            if (!err)
            {
                status = commandTable_.apply(CommandKey,jsonMsg,jsonDat);
            }
            else
            {
                status.success = false;
                status.message = "unable to parse json";
            }
            messageSender_.sendCommandResponse(status,jsonDat);
        }
    }

    

    void SystemState::serviceDataBuffer()
    {
        // Check for last sample flag to see if done
        bool run_complete = false;
        if (lastSampleFlag_)
        {
            run_complete = true;
        }

        // Empty data buffer
        size_t buffer_size;
        ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
        {
            buffer_size = dataBuffer_.size();
        }

        while (buffer_size > 0)
        {
            Sample sample;
            ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
            {
                sample = dataBuffer_.front();
                dataBuffer_.pop_front();
                buffer_size = dataBuffer_.size();
            }
            messageSender_.sendSample(sample);
        }

        // Send indication that the run is complete 
        if (run_complete)
        {
            messageSender_.sendSampleEnd();
            lastSampleFlag_ = false;
        }
    }


    void SystemState::setTestTimerCallback(void(*callback)())
    {
        testTimerCallback_ = callback;
    }


    void SystemState::updateTestOnTimer()
    {
        bool done = false;

        if (test_ == nullptr)
        {
            done = true;
        }
        else
        {
            uint64_t t = uint64_t(TestTimerPeriod)*timerCnt_;
            float volt = test_ -> getValue(t);
            analogSubsystem_.setVolt(volt);
            float curr = analogSubsystem_.getCurr();

            if (timerCnt_ > 0)
            {
                if (test_ -> getSampleMethod() == SampleGeneric)
                {
                    // ------------------------------------------------------------------
                    // Send sample data for tests which use normal sampling 
                    // ------------------------------------------------------------------
                    if (timerCnt_%sampleModulus_ == 0)
                    {
                        Sample sample = {t, volt, curr};
                        dataBuffer_.push_back(sample);
                    }
                }
                else
                {
                    // ------------------------------------------------------------------
                    // Send sample for tests which use custom sampling methods
                    // ------------------------------------------------------------------
                    Sample sampleRaw  = {t, volt, curr}; // Raw sample data
                    dataBuffer_.push_back(sampleRaw);
                    Sample sampleTest = {0, 0.0, 0.0}; // Custom sample data (set in updateSample)
                    //dataBuffer_.push_back(sampleRaw);
                    if (test_ -> updateSample(sampleRaw, sampleTest))
                    {
                        //dataBuffer_.push_back(sampleTest);
                    }
                }
            }
            done = test_ -> isDone(t);
            timerCnt_++;
        }

        if (done) 
        {
            stopTest();
        }
    }


    void SystemState::startTest()
    {
        if (test_ != nullptr)
        {
            timerCnt_ = 0;

            test_ -> reset();

            testInProgress_ = true;
            testTimer_.begin(testTimerCallback_, TestTimerPeriod);
        }
    }


    void SystemState::stopTest()
    {
        testTimer_.end();
        testInProgress_ = false;
        lastSampleFlag_ = true;
    }


    void SystemState::setSamplePeriod(uint32_t samplePeriod)
    {
        samplePeriod_ = constrain(samplePeriod, MinimumSamplePeriod, MaximumSamplePeriod);
        updateSampleModulus();
        voltammetry_.setSamplePeriod(uint64_t(samplePeriod_));
    }


    uint32_t SystemState::getSamplePeriod()
    {
        return samplePeriod_;
    }


    void SystemState::updateSampleModulus()
    {
        sampleModulus_ = samplePeriod_/TestTimerPeriod;
    }

}

