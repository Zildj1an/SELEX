#ifndef ___PCR_WIFI_COMMUNICATOR___
#define ___PCR_WIFI_COMMUNICATOR___
 
#include "communicator.h"

typedef void (t_network_receive_interface)();
typedef void (t_network_send_interface)(char *response, char *funcName);

class WifiCommunicator: public Communicator {

public:
  WifiCommunicator(t_network_receive_interface receive, t_network_send_interface send);
  void ResetCommand();
  void RequestStatus();
  void SendCommand();
  void AddCommandParam (const char *key, const char *value, char *debug);

protected:
  boolean ParseWholeMessage();
  void SendRequestResponse();
  void SendCommandResponse();
  void SendStatusResponse(char *response, int size);
  void OnFinishReaing();

private:
  t_network_receive_interface *networkReceiveInterface;
  t_network_send_interface *networkSendInterface;
  boolean isReading = false;
  boolean hasMessage = false;
  char *paramPtr;
};

#endif /* ___PCR_WIFI_COMMUNICATOR___ */
