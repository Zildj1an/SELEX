#ifndef PS_SYSTEM_STATE_H
#define PS_SYSTEM_STATE_H

#include <Arduino.h>
#include "ps_constants.h"
#include "ps_return_status.h"
#include "ps_analog_subsystem.h"
#include "ps_message_receiver.h"
#include "ps_message_sender.h"
#include "ps_message_parser.h"
#include "ps_command_table.h"
#include "ps_circular_buffer.h"
#include "ps_voltammetry.h"
#include "ps_sample.h"
#include "ps_filter.h"
#include "third-party/Array/Array.h"
#define ARDUINOJSON_USE_DOUBLE 0
#include "third-party/ArduinoJson/ArduinoJson.h"

namespace ps
{

    class SystemState
    {

        public:

            SystemState();
            void initialize();

            void processMessages();
            void updateMessageData();
            void serviceDataBuffer();

            ReturnStatus onCommandRunTest(JsonVariant &jsonMsg, JsonVariant &jsonDat);
            ReturnStatus onCommandStopTest(JsonVariant &jsonMsg, JsonVariant &jsonDat);
            ReturnStatus onCommandSetTestParam(JsonVariant &jsonMsg, JsonVariant &jsonDat);
            ReturnStatus onCommandGetTestParam(JsonVariant &jsonMsg, JsonVariant &jsonDat);
            ReturnStatus onCommandSetSamplePeriod(JsonVariant &jsonMsg, JsonVariant &jsonDat);
            ReturnStatus onCommandGetSamplePeriod(JsonVariant &jsonMsg, JsonVariant &jsonDat);
            ReturnStatus onCommandGetTestDoneTime(JsonVariant &jsonMsg, JsonVariant &jsonDat);
            ReturnStatus onCommandGetTestNames(JsonVariant &jsonMsg, JsonVariant &jsonDat);

            void startTest();
            void stopTest();

            void setSamplePeriod(uint32_t samplePeriod);
            uint32_t getSamplePeriod();

            void setTestTimerCallback(void(*func)());
            void updateTestOnTimer();


        protected:

            volatile bool testInProgress_;
            volatile bool lastSampleFlag_;

            MessageReceiver messageReceiver_;
            MessageParser messageParser_;
            MessageSender messageSender_;

            CommandTable<SystemState,CommandTableMaxSize> commandTable_;

            AnalogSubsystem analogSubsystem_;

            CircularBuffer<Sample,DataBufferSize> dataBuffer_;
            Voltammetry voltammetry_;

            IntervalTimer testTimer_;
            void (*testTimerCallback_)() = dummyTimerCallback;
            volatile uint64_t timerCnt_;
            uint32_t samplePeriod_; 
            uint32_t sampleModulus_;  

            float lowPassDtSec_;
            BaseTest *test_;

            static void dummyTimerCallback() {};
            void updateSampleModulus();
    };


} // namespace ps

#endif
