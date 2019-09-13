#include "ps_message_sender.h"
#include "ps_time_utils.h"

namespace ps
{

    MessageSender::MessageSender()
    {}

    void MessageSender::sendCommandResponse(ReturnStatus status, JsonVariant &jsonDat)
    {
        StaticJsonDocument<JsonMessageBufferSize> jsonMsg;
        jsonMsg[SuccessKey].set(status.success);
        if (status.message.length() > 0)
        {
            jsonMsg[MessageKey].set(status.message);
        }
        jsonMsg[ResponseKey].set(jsonDat);
        char output[JsonMessageBufferSize];
        serializeJson(jsonMsg, output);
        Serial.println(output);
    }

    void MessageSender::sendSample(Sample sample)
    {
        StaticJsonDocument<JsonMessageBufferSize> jsonSample;
        jsonSample[TimeKey].set(convertUsToMs(sample.t)); 
        jsonSample[VoltKey].set(sample.volt);
        jsonSample[CurrKey].set(sample.curr);
        char output[JsonMessageBufferSize];
        serializeJson(jsonSample, output);
        Serial.println(output);
    }

    void MessageSender::sendSampleEnd()
    {
        StaticJsonDocument<JsonMessageBufferSize> jsonSample;
        char output[JsonMessageBufferSize];
        serializeJson(jsonSample, output);
        Serial.println(output);
    }

} // namespace ps



// Send time in us as string
// -------------------------------------------------------
//char timeBuf[100]; 
//snprintf(timeBuf,sizeof(timeBuf),"%llu", sample.t);
//jsonRoot[TimeKey] = timeBuf;
// ------------------------------------------------------
