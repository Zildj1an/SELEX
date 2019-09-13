#ifndef PS_KEYVALUE_COMMAND_H
#define PS_KEYVALUE_COMMAND_H

#include "ps_constants.h"

namespace ps
{

    template<typename T>
    class KeyValueCommand
    {
        public:
            KeyValueCommand() {};
            KeyValueCommand(String key, String value, ReturnStatus (T::*method)(JsonVariant&,JsonVariant&));

            String key();
            void setKey(String key);

            String value();
            void setValue(String value);

            void setMethod(ReturnStatus (T::*method)(JsonVariant&,JsonVariant&));
            ReturnStatus applyMethod(T* client, JsonVariant &jsonMsg, JsonVariant &jsonDat);

        protected:
            String key_;
            String value_;
            ReturnStatus (T::*method_)(JsonVariant&,JsonVariant&) = nullptr;
    };


    template<typename T>
    KeyValueCommand<T>::KeyValueCommand(String key, String value, ReturnStatus (T::*method)(JsonVariant&,JsonVariant&))
        : key_(key), value_(value), method_(method) 
    {}


    template<typename T>
    String KeyValueCommand<T>::key()
    {
        return key_;
    }


    template<typename T>
    void KeyValueCommand<T>::setKey(String key)
    {
        key_ = key;
    }


    template<typename T>
    String KeyValueCommand<T>::value()
    {
        return value_;
    }


    template<typename T>
    void KeyValueCommand<T>::setValue(String value)
    {
        value_ = value;
    }


    template<typename T>
    void KeyValueCommand<T>::setMethod(ReturnStatus (T::*method)(JsonVariant&,JsonVariant&))
    {
        method_ = method;
    }


    template<typename T>
    ReturnStatus KeyValueCommand<T>::applyMethod(T *client, JsonVariant &jsonMsg, JsonVariant &jsonDat)
    {
        ReturnStatus status;
        if (method_ != nullptr)
        {
            status = ((*client).*(method_))(jsonMsg,jsonDat);
        }
        else
        {
            status.success = false;
            status.message = "KeyValueCommand: method is nullptr";
        }
        return status;
    }


} // namespace ps

#endif
