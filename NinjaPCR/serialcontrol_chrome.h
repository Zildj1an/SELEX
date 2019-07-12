/*
 *  serialcontrol_chrome.h - OpenPCR control software.
 *  Copyright (C) 2010-2012 Josh Perfetto and Xia Hong. All Rights Reserved.
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

#ifndef _SERIALCONTROL_H_
#define _SERIALCONTROL_H_

#include "communicator.h"

class Display;

typedef enum {
    SERIAL_CONTINUE,
    SERIAL_TIMEOUT,
    SERIAL_RECEIVED
} SERIAL_STATUS;

class SerialControl: public Communicator {

public:
  SerialControl(Display* pDisplay);
  // TODO inherit destructor
protected:
  boolean ParseWholeMessage();
  void SendStatusResponse (char *response, int size);
  void SendCommandResponse ();
  void OnFinishReaing ();

private:
  SERIAL_STATUS ReadPacket(); //returns true if bytes were read

private:
  Display* ipDisplay;
};

#endif
