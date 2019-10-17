#ifndef PS_VOLTAMMETRY_H
#define PS_VOLTAMMETRY_H

#include "ps_constants.h"
#include "ps_return_status.h"
#include "ps_base_test.h"
#include "ps_cyclic_test.h"
#include "ps_sinusoid_test.h"
#include "ps_constant_test.h"
#include "ps_linearsweep_test.h"
#include "ps_multistep_test.h"
#include "ps_squarewave_test.h"

#include "third-party/ArduinoJson/ArduinoJson.h"
#include "third-party/Array/Array.h"

namespace ps
{

    class Voltammetry
    {

        public:

            Voltammetry();

            BaseTest *getTest(String name);
            ReturnStatus getTest(JsonVariant &jsonMsg, JsonVariant &jsonDat, BaseTest* &testPtr);
            ReturnStatus getParam(JsonVariant &jsonMsg, JsonVariant &jsonDat);
            ReturnStatus setParam(JsonVariant &jsonMsg, JsonVariant &jsonDat);
            ReturnStatus getTestDoneTime(JsonVariant &jsonMsg, JsonVariant &jsonDat);
            ReturnStatus getTestNames(JsonVariant &jsonMsg, JsonVariant &jsonDat);
            ReturnStatus getMuxTestNames(JsonVariant &jsonMsg, JsonVariant &jsonDat);

            void setSamplePeriod(uint64_t samplePeriod);

            BaseTest baseTest;
            CyclicTest cyclicTest;
            SinusoidTest sinusoidTest;
            ConstantTest constantTest;
            SquareWaveTest squareWaveTest;
            LinearSweepTest linearSweepTest;

            static const String TestKey;

        protected:

            Array<BaseTest*,AvailableTestsMaxSize> availableTests_;

    };

}

#endif
