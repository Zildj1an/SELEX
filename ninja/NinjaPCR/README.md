# Thermocycler controller

This is the original NinjaPCR software, modified to allow OTA updates and control the automated lid.

The lid will automatically open when the system boots, close when a program starts, and open again when it is completed or stopped.

You can use the OTA updater via "http://\<address\>/update"

NOTE: we were unable to use mDNS to connect to the server, so to control the module you'll have to either use it in AP mode, get your DHCP server to assign it a fixed IP, or manually find the IP address each time using, for example, nmap.

NOTE: For the automated lid to work, a pin must be used to control the servo. Since there are no free pins in the NinjaPCB, we use the least-used one: the RX pin. The downside is that the serial port can no longer be used to communicate with the thermocycler, but maybe you can get it to still transmit debug info over TX. For the moment all uses of the Serial class have been disabled. Change ENABLE_AUTOMATIC_LID in board_conf_ninjapcr_wifi.h to enable Serial again. 
