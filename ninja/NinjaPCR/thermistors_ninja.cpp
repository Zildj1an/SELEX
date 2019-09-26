/*
 *  program.cpp - OpenPCR control software.
 *  Copyright (C) 2010-2012 Josh Perfetto. All Rights Reserved.
 *
 *  OpenPCR control software is free software: you can redistribute it and/or
 *  modify it under the terms of the GNU General Public License as published
 *  by the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  OpenPCR control software is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License along with
 *  the OpenPCR control software.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "pcr_includes.h"
#include "thermistors.h"
#include "adc.h"
#include <Arduino.h>

#ifdef TEHRMISTORS_NINJAPCR

#define THERMISTOR_BASE_TEMP 25.0

#define KELVIN 273.15

// Well Thermistor
#define B_CONST_25_50 4250
#define B_CONST_25_85 4311
#define B_CONST_25_100 4334
#define R_0_WELL 100.0


/*
// 103-JT-025
#define B_CONST_HEATER 3435
#define R_0_HEATER 100.0
*/



// 104-JT-025
#define B_CONST_HEATER 4390
#define R_0_HEATER 100.0 

// Counter resistors
#define R_LOW_TEMP 30.0 // Well low mode
#define R_HIGH_TEMP 10 // Well high mode (30x3)
#define R_HEATER 4.99 // Heater

#define HIGH_LOW_SWITCHING_TEMP 54
//#define PRINT_DEBUG_CHART

static float INVERSE_BASE_TEMP = 1.0 / (THERMISTOR_BASE_TEMP + KELVIN);

double voltageToTemp (double voltageRatio, float resistance, float b_constant, float r0) {
    double thermistorR = resistance * voltageRatio / (1.0 - voltageRatio);
    return (1 / ((log(thermistorR / r0) / b_constant) + INVERSE_BASE_TEMP))  - KELVIN;
}
double tempToVoltageRatio (double tempCelsius, double resistance, double bConst, double r0) {
    double thermistorR = r0 * exp(bConst * (1/(tempCelsius+KELVIN) - 1/(THERMISTOR_BASE_TEMP+KELVIN)));
    return thermistorR/(thermistorR+ resistance);

}

////////////////////////////////////////////////////////////////////
// Class CLidThermistor
static double SWITCHING_VOLTAGE_50_LID = 0;
static double SWITCHING_VOLTAGE_85_LID = 0;

CLidThermistor::CLidThermistor() :
        iTemp(0.0) {
    PCR_DEBUG_LINE("CLidThermistor");

    SWITCHING_VOLTAGE_50_LID = tempToVoltageRatio(50, R_HEATER, B_CONST_25_50, R_0_WELL);
    SWITCHING_VOLTAGE_85_LID = tempToVoltageRatio(85, R_HEATER, B_CONST_25_85, R_0_WELL);
    PCR_DEBUG("Lid 50=");
    PCR_DEBUG_LINE(SWITCHING_VOLTAGE_50_LID);
    PCR_DEBUG("Lid 85=");
    PCR_DEBUG_LINE(SWITCHING_VOLTAGE_85_LID);

#ifdef PRINT_DEBUG_CHART

    for (double v=0; v<1.0; v+=0.05) {
      double b_constant = B_CONST_HEATER;
      double temp = voltageToTemp(v, R_HEATER, b_constant, R_0_HEATER);
      PCR_DEBUG(v);
      PCR_DEBUG("\t");
      PCR_DEBUG_LINE(temp);
    }
#endif /* PRINT_DEBUG_CHART */
}
//------------------------------------------------------------------------------
HardwareStatus CLidThermistor::ReadTemp() {
    double voltageRatio;
    float lidADCValue;
    HardwareStatus result = getLidADCValue(&lidADCValue);
    if (result!=HARD_NO_ERROR) { return result; }
    voltageRatio = 1.0-lidADCValue;
    PCR_ADC_DEBUG("LidR=");
    PCR_ADC_DEBUG_LINE(voltageRatio);
    
    if (voltageRatio < 0.1) {
        // ThermistorR=0 (Short)
        return HARD_ERROR_LID_THERMISTOR_SHORT;
    }
    if (voltageRatio > 0.97) {
        // ThermistorR=INF (Thermistor is disconnected)
        return HARD_ERROR_LID_THERMISTOR_DISCONNECTED;
    }
    float b_constant;
    
    if (voltageRatio > SWITCHING_VOLTAGE_50_LID)
        b_constant = B_CONST_25_50;
    else if (voltageRatio > SWITCHING_VOLTAGE_85_LID)
        b_constant = B_CONST_25_85;
    else
        b_constant = B_CONST_25_100;

    b_constant = B_CONST_HEATER;
    float temp = voltageToTemp (voltageRatio, R_HEATER, b_constant, R_0_HEATER);
    //double thermistorR = resistance * voltageRatio / (1.0 - voltageRatio);
    iTemp = temp;
    return HARD_NO_ERROR;
}

////////////////////////////////////////////////////////////////////
// Class CPlateThermistor
static double SWITCHING_VOLTAGE_50_LOWMODE = 0;
static double SWITCHING_VOLTAGE_85_LOWMODE = 0;
static double SWITCHING_VOLTAGE_50_HIGHMODE = 0;
static double SWITCHING_VOLTAGE_85_HIGHMODE = 0;

void printVoltageTempTable () {
    PCR_DEBUG("SWITCHING_VOLTAGE_50_LOWMODE=");
    PCR_DEBUG_LINE(SWITCHING_VOLTAGE_50_LOWMODE*3.3);
    PCR_DEBUG("SWITCHING_VOLTAGE_85_LOWMODE="); 
    PCR_DEBUG_LINE(SWITCHING_VOLTAGE_85_LOWMODE*3.3);

    PCR_DEBUG("SWITCHING_VOLTAGE_50_HIGHMODE="); PCR_DEBUG_LINE(SWITCHING_VOLTAGE_50_HIGHMODE*3.3);
    PCR_DEBUG("SWITCHING_VOLTAGE_85_HIGHMODE="); PCR_DEBUG_LINE(SWITCHING_VOLTAGE_85_HIGHMODE*3.3);
    double resistance = 0;
    PCR_DEBUG_LINE("HIGH");
    for (double v=0; v<3.3; v+=0.1) {
      double b_constant;
      double voltageRatio = v/3.3;
      resistance = R_HIGH_TEMP;
      if (voltageRatio > SWITCHING_VOLTAGE_50_HIGHMODE)
          b_constant = B_CONST_25_50;
      else if (voltageRatio > SWITCHING_VOLTAGE_85_HIGHMODE)
          b_constant = B_CONST_25_85;
      else
          b_constant = B_CONST_25_100;
      double temp = voltageToTemp (voltageRatio, resistance, b_constant, R_0_WELL);
      PCR_DEBUG(v);PCR_DEBUG("\t");PCR_DEBUG_LINE(temp);
    }
    PCR_DEBUG_LINE("LOW");
    for (double v=0; v<3.3; v+=0.1) {
      double b_constant;
      double voltageRatio = v/3.3;
      resistance = R_LOW_TEMP;
      if (voltageRatio > SWITCHING_VOLTAGE_50_LOWMODE)
          b_constant = B_CONST_25_50;
      else if (voltageRatio > SWITCHING_VOLTAGE_85_LOWMODE)
          b_constant = B_CONST_25_85;
      else
          b_constant = B_CONST_25_100;
      double temp = voltageToTemp (voltageRatio, resistance, b_constant, R_0_WELL);
      PCR_DEBUG(v);PCR_DEBUG("\t");PCR_DEBUG_LINE(temp);
    }

}

CPlateThermistor::CPlateThermistor() :
        iTemp(0.0) {
    // ADC setup
    initADC();

    SWITCHING_VOLTAGE_50_LOWMODE = tempToVoltageRatio(50, R_LOW_TEMP, B_CONST_25_50, R_0_WELL);
    SWITCHING_VOLTAGE_85_LOWMODE = tempToVoltageRatio(85, R_LOW_TEMP, B_CONST_25_85, R_0_WELL);
    SWITCHING_VOLTAGE_50_HIGHMODE = tempToVoltageRatio(50, R_HIGH_TEMP, B_CONST_25_50, R_0_WELL);
    SWITCHING_VOLTAGE_85_HIGHMODE = tempToVoltageRatio(85, R_HIGH_TEMP, B_CONST_25_85, R_0_WELL);

    pinMode(PIN_WELL_HIGH_TEMP, OUTPUT);
    pinMode(PIN_WELL_HIGH_TEMP, LOW);
}
//------------------------------------------------------------------------------

void CPlateThermistor::start() {
    // ADC setup
    initADC();
    
#ifdef PRINT_DEBUG_CHART
    printVoltageTempTable();
#endif
}
bool isHighTempMode = false;

HardwareStatus CPlateThermistor::ReadTemp() {
    float voltageRatio;
    HardwareStatus result = getWellADCValue(&voltageRatio);
    if (result!=HARD_NO_ERROR) { return result; }
    PCR_ADC_DEBUG("WellR=");
    PCR_ADC_DEBUG_LINE(voltageRatio);
    if (voltageRatio < 0.1) {
        return HARD_ERROR_WELL_THERMISTOR_SHORT;
    }
    if (voltageRatio > 0.95 ) {
        return HARD_ERROR_WELL_THERMISTOR_DISCONNECTED;
    }
    float resistance, b_constant;
    if (isHighTempMode) {
        resistance = R_HIGH_TEMP;
        if (voltageRatio > SWITCHING_VOLTAGE_50_LOWMODE)
            b_constant = B_CONST_25_50;
        else if (voltageRatio > SWITCHING_VOLTAGE_85_LOWMODE)
            b_constant = B_CONST_25_85;
        else
            b_constant = B_CONST_25_100;
    } else {
        // Low temp mode (R=16 kOhm)
        resistance = R_LOW_TEMP;
        if (voltageRatio > SWITCHING_VOLTAGE_50_HIGHMODE)
            b_constant = B_CONST_25_50;
        else if (voltageRatio > SWITCHING_VOLTAGE_85_HIGHMODE)
            b_constant = B_CONST_25_85;
        else
            b_constant = B_CONST_25_100;
    }
    float temp = voltageToTemp (voltageRatio, resistance, b_constant, R_0_WELL);
    iTemp = temp;

    // Switch high/low mode (isHighTempMode)
    isHighTempMode = (iTemp > HIGH_LOW_SWITCHING_TEMP);
    pinMode(PIN_WELL_HIGH_TEMP, OUTPUT); //TODO init in starting func
    digitalWrite(PIN_WELL_HIGH_TEMP, isHighTempMode);
    return HARD_NO_ERROR;
}
//------------------------------------------------------------------------------

char CPlateThermistor::SPITransfer(volatile char data) {
#ifndef USE_WIFI
    SPDR = data;                    // Start the transmission
    while (!(SPSR & (1<<SPIF)))// Wait the end of the transmission
    {};
    return SPDR;                    // return the received byte
#endif
}

#endif /* TEHRMISTORS_NINJA */
