#ifndef ___PCR_COMMUNICATOR___
#define ___PCR_COMMUNICATOR___

#include "thermocycler.h"
#include <Arduino.h>

#define START_CODE    0xFF
#define ESCAPE_CODE   0xFE

class ProgramComponent;
class Cycle;
class Step;
struct SCommand;

typedef enum {
    SEND_CMD       = 0x10,
    STATUS_REQ     = 0x40,
    STATUS_RESP    = 0x80
} PACKET_TYPE;

//packet header
struct PCPPacket {
  PCPPacket(PACKET_TYPE type)
  : startCode(START_CODE)
  , length(0)
  , eType(type)
  {}

  uint8_t startCode;
  uint16_t length;
  uint8_t eType; //lower 4 bits are used for seq
};

class Communicator {
public:
  Communicator();
  ~Communicator();

  void ProcessDummyMessage (unsigned char _currentCommand, String command);
  void Process();
  byte* GetBuffer() { return buf; } //used for stored program parsing at start-up only if no serial command received
  boolean CommandReceived() { return iReceivedStatusRequest; }

protected:
  virtual boolean ParseWholeMessage() = 0;
  virtual void SendStatusResponse (char *response, int size) = 0;
  virtual void SendCommandResponse () = 0;
  virtual void OnFinishReaing () = 0;

  void FinishReading ();

  char* AddParam(char* pBuffer, char key, int val, boolean init = false);
  char* AddParam(char* pBuffer, char key, unsigned long val, boolean init = false);
  char* AddParam(char* pBuffer, char key, float val, int decimalDigits, boolean pad, boolean init = false);
  char* AddParam(char* pBuffer, char key, const char* szVal, boolean init = false);
  char* AddParam_P(char* pBuffer, char key, const char* szVal, boolean init = false);

protected:
  unsigned char currentCommand = 0;
  unsigned char commandBody[256];

private:
  void ProcessMessage ();
  void SendStatus ();

  const char* GetProgramStateString_P(Thermocycler::ProgramState state);
  const char* GetThermalStateString_P(Thermocycler::ThermalState state);

private:
  byte buf[MAX_COMMAND_SIZE + 1]; //read or write buffer

  typedef enum{
    STATE_START,
    STATE_STARTCODE_FOUND,
    STATE_PACKETLEN_LOW,
    STATE_PACKETHEADER_DONE
  }PACKET_STATE;

  PACKET_STATE packetState;
  uint8_t lastPacketSeq;
  uint16_t packetLen, packetRealLen, iCommandId;
  boolean bEscapeCodeFound;
  boolean iReceivedStatusRequest;
};

#endif /* ___PCR_COMMUNICATOR___ */
