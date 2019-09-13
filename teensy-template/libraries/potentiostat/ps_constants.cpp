#include "ps_constants.h"
#include "ps_analog_subsystem.h"
#include <initializer_list>

namespace ps
{ 
    const String FirmwareVersion = String("1");

    // Serial parameters
    const uint32_t UsbSerialBaudrate = 115200;

    // Device ID EEPROM address
    extern const uint32_t EEPROM_DeviceIdAddress = 0;

    // Json message keys 
    const String CommandKey = String("command");
    const String ResponseKey = String("response");
    const String MessageKey = String("message");
    const String SuccessKey = String("success");
    const String TimeKey = String("t");
    const String VoltKey = String("v");
    const String CurrKey = String("i");
    const String ChanKey = String("n");
    const String RefVoltKey = String("r");
    const String ParamKey = String("param");
    const String VoltRangeKey = String("voltRange");
    const String CurrRangeKey = String("currRange");
    const String QuietValueKey = String("quietValue"); 
    const String QuietTimeKey = String("quietTime");
    const String DurationKey = String("duration");
    const String ValueKey = String("value");
    const String StartValueKey = String("startValue");
    const String FinalValueKey = String("finalValue");
    const String StepValueKey = String("stepValue");
    const String AmplitudeKey = String("amplitude");
    const String OffsetKey = String("offset");
    const String PeriodKey = String("period");
    const String NumCyclesKey = String("numCycles");
    const String ShiftKey = String("shift");
    const String WindowKey = String("window");
    const String DeviceIdKey = String("deviceId");
    const String SamplePeriodKey = String("samplePeriod");
    const String TestDoneTimeKey = String("testDoneTime");
    const String StepArrayKey = String("step");
    const String TestNameArrayKey = String("testNames");
    const String VersionKey = String("version");
    const String VariantKey = String("variant");
    const String ConnectedKey = String("connected");

    // Json command strings
    const String RunTestCmd = String("runTest");
    const String StopTestCmd = String("stopTest");
    const String GetVoltCmd = String("getVolt");
    const String SetVoltCmd = String("setVolt");
    const String GetCurrCmd = String("getCurr");
    const String SetParamCmd = String("setParam");
    const String GetParamCmd = String("getParam");
    const String SetDeviceIdCmd = String("setDeviceId");
    const String GetDeviceIdCmd = String("getDeviceId");
    const String SetSamplePeriodCmd = String("setSamplePeriod");
    const String GetSamplePeriodCmd = String("getSamplePeriod");
    const String GetTestDoneTimeCmd = String("getTestDoneTime");
    const String GetTestNamesCmd = String("getTestNames");
    const String GetVersionCmd = String("getVersion");
    const String GetVariantCmd = String("getVariant");

    // Ranges for output voltage
    const String VoltageVariant = String("AD8608");
    const VoltRange VoltRange33V(String("3.3V"),0, 3.3, AnalogSubsystem::MaxValueDac);
    VoltRange voltRangeArrayTmp[NumVoltRange] = {VoltRange33V};
    Array<VoltRange,NumVoltRange>  VoltRangeArray(voltRangeArrayTmp);
    const float SignDac = 1;

    const String CurrentVariant = String("milliAmp 33");
    const CurrRange CurrRange33mA("10uA", 0, 3.3,  AnalogSubsystem::MaxValueAin); 
    CurrRange currRangeArrayTmp[NumCurrRange] = {CurrRange33mA};

    const String HardwareVariant = VoltageVariant + String("_") + CurrentVariant;
    Array<CurrRange,NumCurrRange>  CurrRangeArray(currRangeArrayTmp);

    // Timer parameters
    const uint32_t TestTimerPeriod = 200;                // us
    const uint32_t DefaultSamplePeriod = 10000;          // us
    extern const uint32_t MinimumSamplePeriod = 1000;    // us
    extern const uint32_t MaximumSamplePeriod = 1000000; // us

    // Low pass filter params for current samples
    const LowPassParam CurrLowPassParam = {200.0, 0.0, 2}; // cutoff freq (Hz), initial value, order

} // namespace ps
