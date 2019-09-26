#include "ps_analog_subsystem.h"
#include "ps_constants.h"

namespace ps
{
    // AnalogSubsystem public methods
    // --------------------------------------------------------------------------------------------

    AnalogSubsystem::AnalogSubsystem() {}

    void AnalogSubsystem::initialize()
    {
        // Initialize analog input/output subsystem
        analogWriteResolution(DefaultAnalogWriteResolution);
        analogReadResolution(DefaultAnalogReadResolution);
        analogReadAveraging(DefaultAnalogReadAveraging);
        analogReference(DefaultAnalogReference);

        setCurrRange(CurrRangeArray[0]);
        setVoltRange(VoltRangeArray[0]);

        // Set output voltage to zero
        setValueDac(MidValueDac);     
    }


    void AnalogSubsystem::setVolt(float value) 
    {
        // Set working to reference electrode (output) voltage
        setValueDac(voltRange_.valueToInt(SignDac*value));
    }


    float AnalogSubsystem::getVolt() const     
    {
        // Get working to reference electrode (output) voltage setting
        return SignDac*voltRange_.intToValue(valueDac_);
    }


    float AnalogSubsystem::getCurr() const           
    {
        // Get current measurement from working electrode
        return currRange_.intToValue(getTransAmpAin());
    }


    void AnalogSubsystem::setVoltRange(VoltRange range)
    {
        // Set the output voltage range - for working to reference electrode voltage
        // Note, this command will change the VoltGain setting. 
        voltRange_ = range;
    }

    VoltRange AnalogSubsystem::getVoltRange() const
    { 
        // Returns the devices voltage range settings.
        return voltRange_;
    }


    void AnalogSubsystem::setCurrRange(CurrRange range)
    {
        // Set current transimpedance amplifiers current range
        currRange_ = range;
    }


    CurrRange AnalogSubsystem::getCurrRange() const
    {
        // Returns the transimpedance amplifier's current range setting 
        return currRange_;
    }


    ReturnStatus AnalogSubsystem::setVoltRangeByName(String voltRangeName)
    {
        ReturnStatus status;
        bool found = false;
        for (size_t i=0; i<VoltRangeArray.size(); i++)
        {
            if (voltRangeName.equals(VoltRangeArray[i].name()))
            {
                found = true;
                setVoltRange(VoltRangeArray[i]);
            }
        }
        if (!found)
        {
            status.success = false;
            status.message = String("voltRange, ") + voltRangeName + String(", not found");
        }
        return status;
    }


    String AnalogSubsystem::getVoltRangeName() const
    { 
        // Returns a string representation of the voltage range setting
        return voltRange_.name();
    }


    String AnalogSubsystem::getCurrRangeName() const
    {
        // Returns a string representation of the current range
        return currRange_.name();
    }

    ReturnStatus AnalogSubsystem::setCurrRangeByName(String currRangeName)
    {
        ReturnStatus status;
        bool found = false;

        for (size_t i=0; i<CurrRangeArray.size(); i++)
        {
            if (currRangeName.equals(CurrRangeArray[i].name()))
            {
                found = true;
                setCurrRange(CurrRangeArray[i]);
            }
        }
        
        if (!found)
        {
            status.success = false;
            status.message = String("currRange, ") + currRangeName + String(", not found");
        }
        return status;
    }


    // AnalogSubsystem protected methods
    // --------------------------------------------------------------------------------------------


    void AnalogSubsystem::setValueDac(uint16_t value)
    {
        // The value of the output voltage Dac
        valueDac_ = value < MaxValueDac ? value : MaxValueDac;
        analogWrite(DAC_OUT_PIN,valueDac_);
    }


    uint16_t AnalogSubsystem::getValueDac() const
    {
        // Return the value currently used by the output voltage Dac
        return valueDac_;
    }


    uint16_t AnalogSubsystem::getTransAmpAin() const  
    {
        // Read analog input associated with the transimpedance amplifier 
       return analogRead(ADC_INP_PIN);
    }


} // namespace ps
