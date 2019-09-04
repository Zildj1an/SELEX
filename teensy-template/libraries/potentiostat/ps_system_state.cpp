#include "ps_system_state.h"
#include "ps_device_id_eeprom.h"
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
        commandTable_.setClient(this);
        commandTable_.registerMethod(CommandKey,   RunTestCmd,            &SystemState::onCommandRunTest);
        commandTable_.registerMethod(CommandKey,   StopTestCmd,           &SystemState::onCommandStopTest);
        commandTable_.registerMethod(CommandKey,   SetParamCmd,           &SystemState::onCommandSetTestParam);
        commandTable_.registerMethod(CommandKey,   GetParamCmd,           &SystemState::onCommandGetTestParam);
        commandTable_.registerMethod(CommandKey,   SetSamplePeriodCmd,    &SystemState::onCommandSetSamplePeriod);
        commandTable_.registerMethod(CommandKey,   GetSamplePeriodCmd,    &SystemState::onCommandGetSamplePeriod);
        commandTable_.registerMethod(CommandKey,   GetTestDoneTimeCmd,    &SystemState::onCommandGetTestDoneTime);

        messageReceiver_.reset();

    }


    ReturnStatus SystemState::onCommandRunTest(JsonObject &jsonMsg, JsonObject &jsonDat)
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

        if (multiplexer_.isRunning())
        {
            if (!(test_ -> isMuxCompatible()))
            {
                status.success = false;
                status.message = String("test, ") + (test_ -> getName()) + String(", is not mux compatible");
                return status;
            }
            if (multiplexer_.numEnabledWrkElect() <= 0)
            {
                status.success = false;
                status.message = String("mux running, but no enabled working electrode channels");
                return status;
            }
            else
            {
                multiplexer_.connectCtrElect();
                multiplexer_.connectRefElect();
                multiplexer_.connectFirstEnabledWrkElect();
            }
        }

        startTest();
        return status;
    }


    ReturnStatus SystemState::onCommandStopTest(JsonObject &jsonMsg, JsonObject &jsonDat)
    {
        ReturnStatus status;
        stopTest();
        return status;
    }


    ReturnStatus SystemState::onCommandSetTestParam(JsonObject &jsonMsg, JsonObject &jsonDat)
    {
        ReturnStatus status = voltammetry_.setParam(jsonMsg,jsonDat);
        return status;
    }


    ReturnStatus SystemState::onCommandGetTestParam(JsonObject &jsonMsg, JsonObject &jsonDat)
    {
        ReturnStatus status = voltammetry_.getParam(jsonMsg,jsonDat);
        return status;
    }


    ReturnStatus SystemState::onCommandSetSamplePeriod(JsonObject &jsonMsg, JsonObject &jsonDat)
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
                uint32_t samplePeriodMs = jsonMsg.get<uint32_t>(SamplePeriodKey);
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
                    jsonDat.set(SamplePeriodKey,convertUsToMs(getSamplePeriod()));
                }
            }
        }
        return status;
    }


    ReturnStatus SystemState::onCommandGetSamplePeriod(JsonObject &jsonMsg, JsonObject &jsonDat)
    {
        ReturnStatus status;
        jsonDat.set(SamplePeriodKey,convertUsToMs(getSamplePeriod()));
        return status;
    }

    
    ReturnStatus SystemState::onCommandGetTestDoneTime(JsonObject &jsonMsg, JsonObject &jsonDat)
    {
        ReturnStatus status;
        status = voltammetry_.getTestDoneTime(jsonMsg, jsonDat);
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
            StaticJsonBuffer<JsonMessageBufferSize> messageJsonBuffer;
            StaticJsonBuffer<JsonMessageBufferSize> commandRespJsonBuffer;

            String message = messageReceiver_.next();
            JsonObject &jsonMsg = messageParser_.parse(message,messageJsonBuffer);

            JsonObject &jsonDat = commandRespJsonBuffer.createObject();
            if (jsonMsg.success())
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

            int electNum = 0; // Default value (0 is non mux channel)
            int electInd = 0; // Default value 

            if (multiplexer_.isRunning())
            {
                electNum = multiplexer_.currentWrkElect();
                electInd = multiplexer_.electNumToIndex(electNum);
            }

            currLowPass_[electInd].update(curr,lowPassDtSec_);

            if (timerCnt_ > 0)
            {
                if (test_ -> getSampleMethod() == SampleGeneric)
                {
                    // ------------------------------------------------------------------
                    // Send sample data for tests which use normal sampling 
                    // ------------------------------------------------------------------
                    if (timerCnt_%sampleModulus_ == 0)
                    {
                        Sample sample = {t, volt, currLowPass_[electInd].value(),uint8_t(electNum)};
                        dataBuffer_.push_back(sample);
                        if (multiplexer_.isRunning())
                        {
                            multiplexer_.connectNextEnabledWrkElect();   
                        }
                    }
                }
                else
                {
                    // ------------------------------------------------------------------
                    // Send sample for tests which use custom sampling methods
                    // ------------------------------------------------------------------
                    Sample sampleRaw  = {t, volt, currLowPass_[0].value(),uint8_t(electNum)}; // Raw sample data
                    Sample sampleTest = {0, 0.0, 0.0, uint8_t(electNum)}; // Custom sample data (set in updateSample)
                    if (test_ -> updateSample(sampleRaw, sampleTest))
                    {
                        dataBuffer_.push_back(sampleTest);
                        if (multiplexer_.isRunning())
                        {
                            multiplexer_.connectNextEnabledWrkElect();   
                        }
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
            analogSubsystem_.autoVoltRange(test_ -> getMinValue(), test_ -> getMaxValue());

            test_ -> reset();
            if (multiplexer_.isRunning())
            {
                for (int i=0; i<NumMuxChan; i++)
                {
                    currLowPass_[i].reset();
                }
                lowPassDtSec_ = (1.0e-6*TestTimerPeriod)*float(multiplexer_.numEnabledWrkElect());    
            }
            else
            {
                currLowPass_[0].reset();
                lowPassDtSec_ = 1.0e-6*TestTimerPeriod;    
            }

            testInProgress_ = true;
            testTimer_.begin(testTimerCallback_, TestTimerPeriod);
        }
    }


    void SystemState::stopTest()
    {
        testTimer_.end();
        testInProgress_ = false;
        lastSampleFlag_ = true;
        analogSubsystem_.setVolt(0.0);

        if (multiplexer_.isRunning())
        {
            multiplexer_.disconnectWrkElect();
            multiplexer_.disconnectRefElect();
            multiplexer_.disconnectCtrElect();
        }
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

