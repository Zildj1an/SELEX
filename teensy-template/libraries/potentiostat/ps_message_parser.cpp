#include "ps_message_parser.h"

namespace ps
{ 
    MessageParser::MessageParser()
    { }

    DeserializationError MessageParser::parse(String &message, StaticJsonDocument<JsonMessageBufferSize> &jsonBuffer)
    { 
        return deserializeJson(jsonBuffer, (char *)(message.c_str()));
    }

} // namespace ps
