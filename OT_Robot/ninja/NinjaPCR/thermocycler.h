/*
 *  thermocycler.h - OpenPCR control software.
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

#ifndef _THERMOCYCLER_H_
#define _THERMOCYCLER_H_

#include <Arduino.h>
#include "PID_v1.h"
#include "pid.h"
#include "program.h"
#include "thermistors.h"
#include "adc.h"

class Display;
class SerialControl;
class WifiCommunicator;
class Communicator;
void initHardware();
const int CyclerStatusBuffSize = 10;
class Thermocycler {
public:
  enum ProgramState {
    EStartup = 0,
    EStopped,
    ELidWait,
    ERunning,
    EComplete,
    EError,
    EClear //for Display clearing only
  };

  enum ThermalState {
    EHolding = 0,
    EHeating,
    ECooling,
    EIdle
  };

  enum ThermalDirection {
    OFF = 0,
    HEAT,
    COOL
  };

  enum ControlMode {
    EBangBang,
    EPIDLid,
    EPIDPlate
  };

  enum LidState {
	OPEN = 0,
	CLOSED = 1
  };

  Thermocycler();
  Thermocycler(boolean restarted);
  ~Thermocycler();

  // accessors
  ProgramState GetProgramState() { return iProgramState; }
  ThermalState GetThermalState();
  Step* GetCurrentStep() { return ipCurrentStep; }
  Cycle* GetDisplayCycle() { return ipDisplayCycle; }
  int GetTotalCycleIndex();
  int GetTotalCycleCount();
  int GetNumCycles();
  int GetCurrentCycleNum();
  int GetErrorCode() { return iHardwareStatus; }
  const char* GetProgName() { return iszProgName; }
  Display* GetDisplay() { return ipDisplay; }
  ProgramComponentPool<Cycle, 6>& GetCyclePool() { return iCyclePool; }
  ProgramComponentPool<Step, 20>& GetStepPool() { return iStepPool; }
  void SetCommunicator(Communicator *comm);

  boolean Ramping() { return iRamping; }
  boolean Paused() { return iPaused; }
  int GetPeltierPwm() { return iPeltierPwm; }
  double GetLidTemp() { return iLidThermistor.GetTemp(); }
  double GetPlateTemp() { return iPlateThermistor.GetTemp(); }
  double GetTemp () { return iEstimatedSampleTemp; }
  double GetPlateResistance() { return iPlateThermistor.GetResistance(); }
  unsigned long GetTimeRemainingS() { return iEstimatedTimeRemainingS; }
  unsigned long GetElapsedTimeS() { return (millis() - iProgramStartTimeMs) / 1000; }
  unsigned long GetRampElapsedTimeMs() { return iRampElapsedTimeMs; }
  boolean InControlledRamp() { return iRamping && ipCurrentStep->GetRampDurationS() > 0 && ipPreviousStep != NULL; }

  int getAnalogValuePeltier() { return analogValuePeltier; }
  int getAnalogValueLid() { return analogValueLid; }

  LidState GetLidState() { return iLidState; }

  // control
  void SetProgram(Cycle* pProgram, Cycle* pDisplayCycle, const char* szProgName, int lidTemp); //takes ownership of cycles
  void Stop();
  boolean Pause();
  boolean Resume();
  boolean NextStep();
  boolean NextCycle();
  PcrStatus Start();
  boolean SetLidState(LidState st);
  void ProcessCommand(SCommand& command);

  // internal
  boolean Loop();
  void PauseHeatUnits();
  void SetPowerOutputRatio(double newValue);
private:
  struct CyclerStatus {
      long timestamp;
      float lidTemp;
      float wellTemp;
      int lidOutput;
      int wellOutput;
      HardwareStatus hardwareStatus;
  };
private:
  void ReadLidTemp();
  void ReadPlateTemp();
  void CalcPlateTarget();
  void ControlPeltier();
  void ControlLid();
  void PreprocessProgram();
  void UpdateEta();
  void CheckHardware(float *lidTemp, float *wellTemp);

  //util functions
  void AdvanceToNextStep();
  void AdvanceToNextCycle();
  void PrepareStep();
  void SetPlateControlStrategy();
  void SetPeltier(ThermalDirection dir, int pwm);
  void SetLidOutput(int drive);
public:
  Communicator* ipCommunicator;
private:
  // components
  Display* ipDisplay;
  CLidThermistor iLidThermistor;
  CPlateThermistor iPlateThermistor;
  ProgramComponentPool<Cycle, 6> iCyclePool;
  ProgramComponentPool<Step, 20> iStepPool;

  // state
  ProgramState iProgramState;
  double iTargetPlateTemp;
  double iTargetLidTemp;
  double iEstimatedSampleTemp;
  boolean iTempUpdated;
  Cycle* ipProgram;
  Cycle* ipDisplayCycle;
  char iszProgName[21];
  Step* ipPreviousStep;
  Step* ipCurrentStep;
  unsigned long iCycleElapsedTimeMs;
  boolean iRamping;
  boolean iPaused;
  double iPauseTemp;
  boolean iDecreasing;
  boolean iRestarted;
  boolean iNextStepPending;
  boolean iNextCyclePending;

  unsigned int iPrevLoopStartTimeMs;

  ControlMode iPlateControlMode;
  HardwareStatus iHardwareStatus;
  LidState iLidState;

  // Log buffer
  CyclerStatus statusBuff[CyclerStatusBuffSize];
  int statusIndex; // Index of satus ring buffer
  int statusCount; // Total count of status log

  // peltier control
  PID iPlatePid;
  CPIDController iLidPid;
  ThermalDirection iThermalDirection; //holds actual real-time state
  double iPeltierPwm;

  // program eta calculation
  unsigned long iProgramStartTimeMs;
  unsigned long iProgramHoldDurationS;

  double iPowerOutputRatio;

  unsigned long iProgramControlledRampDurationS;
  double iProgramFastRampDegrees;
  double iElapsedFastRampDegrees;
  unsigned long iTotalElapsedFastRampDurationMs;

  //Time of lid warming
  unsigned long iLidWarmStart = 0;

  double iRampStartTemp;
  unsigned long iRampElapsedTimeMs;
  unsigned long iEstimatedTimeRemainingS;
  boolean iHasCooled;
  int analogValuePeltier;
  int analogValueLid;
};

#endif
