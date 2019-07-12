#include "pcr_includes.h"
#include "communicator.h"

#include "thermocycler.h"
#include "program.h"
#include "thermistors.h"

Communicator::Communicator() :
    packetState(STATE_START), packetLen(0), packetRealLen(
        0), lastPacketSeq(0xff), bEscapeCodeFound(false), iCommandId(0), iReceivedStatusRequest(
        false) {
}

Communicator::~Communicator() {
}


const char STOPPED_STR[] PROGMEM = "stopped";
const char LIDWAIT_STR[] PROGMEM = "lidwait";
const char RUNNING_STR[] PROGMEM = "running";
const char COMPLETE_STR[] PROGMEM = "complete";
const char STARTUP_STR[] PROGMEM = "startup";
const char ERROR_STR[] PROGMEM = "error";
const char PAUSED_STR[] PROGMEM = "paused";

void Communicator::Process() {
  boolean contentReceived = ParseWholeMessage();
  if (contentReceived) {
    ProcessMessage();
    FinishReading();
  }
}

/////////////////////////////////////////////////////////////////
// Private

void Communicator::FinishReading() {
  currentCommand = 0;
  OnFinishReaing();
}

void Communicator::ProcessMessage() {
  char* pCommandBuf;
  switch (currentCommand) {
  case SEND_CMD:
    PCR_DEBUG_LINE("ProcessMessage SEND_CMD");
    SCommand command;
    pCommandBuf = (char*) (commandBody);

    //store start commands for restart
    //ProgramStore::StoreProgram(pCommandBuf); TODO
    CommandParser::ParseCommand(command, pCommandBuf);
    GetThermocycler().ProcessCommand(command);
    iCommandId = command.commandId;
    SendCommandResponse();
    break;

  case STATUS_REQ:
    PCR_DEBUG_LINE("ProcessMessage STATUS_REQ");
    iReceivedStatusRequest = true;
    SendStatus();
    break;
  default:
    break;
  }
}

// For testing with demo profile
void Communicator::ProcessDummyMessage (unsigned char _currentCommand, String command) {
    currentCommand = _currentCommand;
    char *str = (char *)malloc(250*sizeof(char));
    command.toCharArray(str, min(command.length(), 256));
    for (int i=0; i<256; i++) {
      commandBody[i] = (unsigned char)str[i];
    }
    free(str);
    ProcessMessage();
    FinishReading();
}

#define STATUS_FILE_LEN 128
void Communicator::SendStatus() {
  Thermocycler::ProgramState state = GetThermocycler().GetProgramState();
  const char* szStatus = (GetThermocycler().Paused())? PAUSED_STR : GetProgramStateString_P(state);
  const char* szThermState = GetThermalStateString_P(
      GetThermocycler().GetThermalState());

  char statusBuf[STATUS_FILE_LEN];
  char* statusPtr = statusBuf;
  Thermocycler& tc = GetThermocycler();

  statusPtr = AddParam(statusPtr, 'd', (unsigned long) iCommandId, true);
  statusPtr = AddParam_P(statusPtr, 's', szStatus);
  statusPtr = AddParam(statusPtr, 'l', tc.GetLidTemp(), 1, false); // float value
  statusPtr = AddParam(statusPtr, 'b', tc.GetPlateTemp(), 1, false);
  statusPtr = AddParam_P(statusPtr, 't', szThermState);

  if (state == Thermocycler::ERunning || state == Thermocycler::EComplete) {
    statusPtr = AddParam(statusPtr, 'e', tc.GetElapsedTimeS());
    statusPtr = AddParam(statusPtr, 'r', tc.GetTimeRemainingS());

    // Total cycles
    statusPtr = AddParam(statusPtr, 'i', tc.GetTotalCycleIndex());
    statusPtr = AddParam(statusPtr, 'a', tc.GetTotalCycleCount());

    // Progress of current cycle
    statusPtr = AddParam(statusPtr, 'u', tc.GetNumCycles());
    statusPtr = AddParam(statusPtr, 'c', tc.GetCurrentCycleNum());
    //statusPtr = AddParam(statusPtr, 'n', tc.GetProgName());
    if (tc.GetCurrentStep() != NULL)
      statusPtr = AddParam(statusPtr, 'p', tc.GetCurrentStep()->GetName());
  }

  else if (state == Thermocycler::EIdle) {
    statusPtr = AddParam(statusPtr, 'v', OPENPCR_FIRMWARE_VERSION_STRING);
  } else if (state == Thermocycler::EError) {
      statusPtr = AddParam(statusPtr, 'w', tc.GetErrorCode());
  }

  statusPtr = AddParam(statusPtr, 'x', tc.getAnalogValueLid()); // Hardware output
  statusPtr = AddParam(statusPtr, 'y', tc.getAnalogValuePeltier()); // Hardware output
  statusPtr = AddParam(statusPtr, 'z', tc.GetTemp(), 1, false); // Sample temp
  statusPtr = AddParam(statusPtr, 'w', tc.GetLidState()); // Lid state
  statusPtr++; //to include null terminator

  int statusBufLen = statusPtr - statusBuf;
  SendStatusResponse(statusBuf, statusBufLen);
}

char* Communicator::AddParam(char* pBuffer, char key, int val, boolean init) {
  if (!init) {
    *pBuffer++ = '&';
  }
  *pBuffer++ = key;
  *pBuffer++ = '=';
  itoa(val, pBuffer, 10);
  while (*pBuffer != '\0')
    pBuffer++;

  return pBuffer;
}

char* Communicator::AddParam(char* pBuffer, char key, unsigned long val,
    boolean init) {
  if (!init) {
    *pBuffer++ = '&';
  }
  *pBuffer++ = key;
  *pBuffer++ = '=';
  ultoa(val, pBuffer, 10);
  while (*pBuffer != '\0')
    pBuffer++;

  return pBuffer;
}

char* Communicator::AddParam(char* pBuffer, char key, float val,
    int decimalDigits, boolean pad, boolean init) {
  if (!init) {
    *pBuffer++ = '&';
  }
  *pBuffer++ = key;
  *pBuffer++ = '=';
  sprintFloat(pBuffer, val, decimalDigits, pad);
  while (*pBuffer != '\0')
    pBuffer++;

  return pBuffer;
}

char* Communicator::AddParam(char* pBuffer, char key, const char* szVal,
    boolean init) {
  if (!init) {
    *pBuffer++ = '&';
  }
  *pBuffer++ = key;
  *pBuffer++ = '=';
  strcpy(pBuffer, szVal);
  while (*pBuffer != '\0')
    pBuffer++;

  return pBuffer;
}

char* Communicator::AddParam_P(char* pBuffer, char key, const char* szVal,
    boolean init) {
  if (!init) {
    *pBuffer++ = '&';
  }
  *pBuffer++ = key;
  *pBuffer++ = '=';
  strcpy_P(pBuffer, szVal);
  while (*pBuffer != '\0')
    pBuffer++;

  return pBuffer;
}

const char* Communicator::GetProgramStateString_P(
    Thermocycler::ProgramState state) {
  switch (state) {
  case Thermocycler::EStopped:
    return STOPPED_STR;
  case Thermocycler::ELidWait:
    return LIDWAIT_STR;
  case Thermocycler::ERunning:
    return RUNNING_STR;
  case Thermocycler::EComplete:
    return COMPLETE_STR;
  case Thermocycler::EStartup:
    return STARTUP_STR;
  case Thermocycler::EError:
    return ERROR_STR;
  default:
    return ERROR_STR;
  }
}

const char HEATING_STR[] PROGMEM = "heating";
const char COOLING_STR[] PROGMEM = "cooling";
const char HOLDING_STR[] PROGMEM = "holding";
const char IDLE_STR[] PROGMEM = "idle";
const char* Communicator::GetThermalStateString_P(
    Thermocycler::ThermalState state) {
  switch (state) {
  case Thermocycler::EHeating:
    return HEATING_STR;
  case Thermocycler::ECooling:
    return COOLING_STR;
  case Thermocycler::EHolding:
    return HOLDING_STR;
  case Thermocycler::EIdle:
    return IDLE_STR;
  default:
    return ERROR_STR;
  }
}
