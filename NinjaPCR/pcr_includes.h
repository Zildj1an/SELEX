/*
 *  pcr_includes.h - OpenPCR control software.
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

#ifndef _PCR_INCLUDES_H_
#define _PCR_INCLUDES_H_

#include "Arduino.h"
#include "board_conf.h"

/* Debug on/off */
#define DEBUG 1

#define DEBUG_ADC /* Debug ADC */
// #define DEBUG_NETWORK /* Debug Network Status */
// TODO DEBUG_TEMPERATURE
// TODO_DEBUG_HARDWARE_OUTPUT

#ifdef DEBUG
 #define PCR_DEBUG(x)  Serial.print (x)
 #define PCR_DEBUG_LINE(x)  Serial.println (x)
#else
 #define PCR_DEBUG(x)
 #define PCR_DEBUG_LINE(x)
#endif

#ifdef DEBUG_ADC
  #define PCR_ADC_DEBUG(x) PCR_DEBUG(x)
  #define PCR_ADC_DEBUG_LINE(x) PCR_DEBUG_LINE(x)
#else
  #define PCR_ADC_DEBUG(x)
  #define PCR_ADC_DEBUG_LINE(x)
#endif


#ifdef DEBUG_NETWORK
  #define PCR_NETWORK_DEBUG(x) PCR_DEBUG(x)
  #define PCR_NETWORK_DEBUG_LINE(x) PCR_DEBUG_LINE(x)
#else
  #define PCR_NETWORK_DEBUG(x)
  #define PCR_NETWORK_DEBUG_LINE(x)
#endif


#define SERIAL_PREFIX "pcr"
#define OPENPCR_FIRMWARE_VERSION_STRING "1.2"
#define FIRMWARE_VERSION_DESCRIPTION "NinjaPCR_v1.2"

#ifndef USE_WIFI
#include <avr/pgmspace.h>
#endif

#define min(a,b) ((a)<(b)?(a):(b))
#define max(a,b) ((a)>(b)?(a):(b))

/* Addresses of WiFi configuration */
/* Wfite 0xF0 when WiFi configuration is done. */

#define EEPROM_WIFI_CONF_DONE_ADDR 512
#define EEPROM_WIFI_CONF_DONE_VAL 0xF0

#define EEPROM_WIFI_SSID_ADDR (EEPROM_WIFI_CONF_DONE_ADDR+1)
#define EEPROM_WIFI_SSID_MAX_LENGTH 31

#define EEPROM_WIFI_PASSWORD_ADDR (EEPROM_WIFI_SSID_ADDR+EEPROM_WIFI_SSID_MAX_LENGTH+1)
#define EEPROM_WIFI_PASSWORD_MAX_LENGTH 31

#define EEPROM_WIFI_MDNS_HOST_ADDR (EEPROM_WIFI_PASSWORD_ADDR+EEPROM_WIFI_PASSWORD_MAX_LENGTH+1)
#define EEPROM_WIFI_MDNS_HOST_MAX_LENGTH 31

#define EEPROM_WIFI_RESULT (EEPROM_WIFI_MDNS_HOST_ADDR+EEPROM_WIFI_MDNS_HOST_MAX_LENGTH+1)

#define EEPROM_OTA_TYPE_ADDR (EEPROM_WIFI_RESULT+1)
#define EEPROM_OTA_CURRENT_VERSION_ADDR (EEPROM_OTA_TYPE_ADDR+1)
#define EEPROM_OTA_CURRENT_VERSION_MAXLENGTH 31

#define PLATE_FAST_RAMP_THRESHOLD_MS 1000

class Thermocycler;
extern Thermocycler* gpThermocycler;
inline Thermocycler& GetThermocycler() { return *gpThermocycler; }

//fixes for incomplete C++ implementation, defined in util.cpp
void* operator new(size_t size);
void operator delete(void * ptr);
extern "C" void __cxa_pure_virtual(void);

//defines
#define STEP_NAME_LENGTH       14
#define MAX_CYCLE_ITEMS        16
#define MAX_COMMAND_SIZE      256

enum PcrStatus {
  ESuccess = 0,
  ETooManySteps = 32,
  ENoProgram,
  ENoPower
};

#define SUCCEEDED(status) (status == ESuccess)

void sprintFloat(char* str, float val, int decimalDigits, boolean pad);
unsigned short htons(unsigned short val);
double absf(double val);
char* rps(const char* progString);

#endif
