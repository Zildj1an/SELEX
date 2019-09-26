#include "wifi_communicator.h"

WifiCommunicator::WifiCommunicator(t_network_receive_interface receive, t_network_send_interface send)
: Communicator () {
  networkReceiveInterface = receive;
  networkSendInterface = send;
}
 

boolean WifiCommunicator::ParseWholeMessage() {
  if (networkReceiveInterface) {
    networkReceiveInterface();
  }
  return hasMessage;
}
void WifiCommunicator::SendCommandResponse () {
  networkSendInterface("true", "command");
}
void WifiCommunicator::SendStatusResponse(char *response, int size) {
  if (networkSendInterface) {
    char *content = (char *) malloc (sizeof(char) * (strlen(response)+3));
    sprintf(content, "\"%s\"", response);
    networkSendInterface(content, "status");
    free(content);
  }
}

void WifiCommunicator::OnFinishReaing() {

}

void WifiCommunicator::ResetCommand() {
  isReading = false;
  hasMessage = false;
}
void WifiCommunicator::RequestStatus() {
  currentCommand = STATUS_REQ;
  hasMessage = true;
}
void WifiCommunicator::SendCommand() {
  currentCommand = SEND_CMD;
  hasMessage = true;
}
void WifiCommunicator::AddCommandParam (const char *key, const char *value, char *debug) {
  if (isReading) {
    *paramPtr++ = '&';
  } else {
    // Reset pointer
    paramPtr = (char *)commandBody;
    
  }
  strcpy(paramPtr, key);
  while (*paramPtr != '\0') {
    paramPtr++;
  }
  *paramPtr++ = '=';
  strcpy(paramPtr, value);
  while (*paramPtr != '\0') {
    paramPtr++;
  }
  strcpy(debug, (const char*)commandBody);
  isReading = true;

}
