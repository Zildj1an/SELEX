# Thermal module controller

This is the original NinjaPCR software, modified to allow OTA updates and work without the lid thermistor and controller.

You can load any program that the NinjaPCR will accept, it will just ignore the lid temperature setting.

You can use the OTA updater via "http://\<address\>/update"

NOTE: we were unable to use mDNS to connect to the server, so to control the module you'll have to either use it in AP mode, get your DHCP server to assign it a fixed IP, or manually find the IP address each time using, for example, nmap.
