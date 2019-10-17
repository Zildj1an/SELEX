# SELEX Process with Artificial Intelligence 👨‍🔧

![version](https://img.shields.io/badge/version-1-blue.svg?cacheSeconds=2592000) [![Website shields.io](https://img.shields.io/website-up-down-green-red/http/shields.io.svg)](https://2019.igem.org/Team:MADRID_UCM/Landing)
[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](http://perso.crans.org/besson/LICENSE.html)

## [0] Introduction 📄

This was a long project that involved:

 * [1] The robotic automatization of biotechnological protocols
 * [2] The usage of Artifical Intelligence
 * [3] A search engine 
 * [4] And many, many custom hardware
 * A website design

You can find information on installation and usage at the end [5]

## [1] Biotechnological Designs 🔬

Folder OT_Robot contains biotechnological protocols for obtaining trained libraries of DNA aptamer molecules automated with the Opentrons OT-2 robot. This protocol is part of our contribution to the 2019 iGEM international biotechnology competition. For the thermocycler we built the Ninja-PCR. More information about the entire project can be found in our <a href = "https://2019.igem.org/Team:MADRID_UCM/Landing">website</a>.

The small-sized thermal cycler is controlled via motherboard Ninja-PCR Arduino-alike, as shown above, manually welded, whose code is in NinjaPCR [folder](https://github.com/Zildj1an/SELEX/tree/master/NinjaPCR). You can update a new binary since ESP8266 SystemOnChip includes the TCP/IP stack. We also recommend the usage of an external Raspberry Pi to uninterruptedly provide the robot with Wi-Fi. You can find more information about usage at [5].

<img src="https://github.com/Zildj1an/SELEX/blob/master/OT_Robot/img/robot.jpg" alt="" width="350"/> <img src="https://github.com/Zildj1an/SELEX/blob/master/OT_Robot/img/ninja.png" alt="" width="445"/>

###  The SELEX Process 🌿
Aptamers are a cutting-edge technology that is revolutionizing biotechnology, from biosensing to synthetic biology. Aptamers are single-strand DNA molecules that hold nature’s most important information: our genetic code. But instead of using DNA for carrying information, our aptamers depend on DNA’s 3-dimensional shape. 

We genetically engineer this shape to take hold of and mesh with our target molecule. DNA’s unique role in nature gives aptamers amazing characteristics, making them robust, stable, and cheap to produce. 

<p align="center"><img src="https://github.com/Zildj1an/SELEX/blob/master/OT_Robot/img/aptameros.png" alt="" width="400"/></p>

_The SELEX process_

## [2] Artificial Intelligence Algorithm: GAN network 🤖

We also did an **Artificial Intelligence algorithm** to predict the optimal DNA molecule shapes. It is a Generative adversarial network, divided in two neuronal networks: the Generative and the Discriminative. CNN nets are used. 

<p align="center"><img src="https://github.com/Zildj1an/SELEX/blob/master/OT_Robot/img/molecule2.gif" alt="" width="400"/></p>

_Generated aptamer_

## [3] iGem Search Engine 🔍 

In addition, you can use our <a href="https://github.com/Zildj1an/iGem_search_engine">search engine</a> for words in previous or this wear team's websites. This is a python search engine with GUI for searching words in each competition year and team's website.

<p align="center"><img src="https://github.com/Zildj1an/SELEX/blob/master/iGem_Search_Engine/search.png" alt="" width="400"/></p>

## [4] Other suggested custom hardware 🔋 

We also handcrafted some modules from ourselves to make things easier and make them fit in the robot. We used a 3D-printer for some of our designs to store Eppendorf and Falcon tipracks. We also deisgned a PCB for a potenciostat microcontroller Teensy 3.0 and an auxiliar thermic module to cool to 4 degrees Celsius, and so on.

The 3D-designs will be made available for public use at https://cad.onshape.com/documents?nodeId=a2079861d9f4b3ba70dc3807&resourceType=folder

<img src="https://github.com/Zildj1an/SELEX/blob/master/OT_Robot/img/potencio.png" alt="" width="350" height = "320"/> <img src="https://github.com/Zildj1an/SELEX/blob/master/OT_Robot/img/termaux.png" alt="" width="350" height = "320"/>
<p align="center"><img src="https://github.com/Zildj1an/SELEX/blob/master/OT_Robot/img/custom_print.png" alt="" width="350"/></p>

## [5] Installation and Usage ❓

You can clone this repo or download the zip. Make sure all the dependencies are covered. First line is for installation of pip at most Linux distributions.

```
$ sudo apt install python-pip || pacman -S python-pip
$ sudo pip install opentrons subprocess time os
```
The robot uses the audio robot.mp3 and gets it from Robot Raspberry's /mnt/usbdrive/ (put it there or edit the location).
You can load the protocol in the Opentrons application, available <a href = "https://opentrons.com/ot-app">here</a>.
We also recommend the usage of an external Raspberry Pi to uninterruptedly provide the robot with Wi-Fi. Once you have stablished the Wi-Fi network at the Raspberry, you can connect the Robot too:

```
# nmcli dev wifi connect <userSSID> password <passwdSSID>
```
After the last update of the Robot -by the time this is written- the SSH connection has changed and now you need to exchange with it a public key for a more secure connection. Then when connected the robot will request the passphrase, at least the first time. Here is how you create the public key (you probably already have one):

```
$ ssh-keygen
Generating public/private rsa key pair.
Enter file in which to save the key (/home/.ssh/id_rsa):
/home/pepe/.ssh/id_rsa already exists.
Overwrite (y/n)?
Enter passphrase (empty for no passphrase):
Your identification has been saved in /home/.ssh/id_rsa.
Your public key has been saved in /home/.ssh/id_rsa.pub.
The key fingerprint is:
a9:49:2e:2a:5e:33:3e:a9:de:4e:77:11:58:b6:90:26 pepe@remote_host
The key's randomart image is:
+--[ RSA 2048]----+
|     ..o         |
|   E o= .        |
|    o. o         |
|        ..       |
|      ..S        |
|     o o.        |
|   =o.+.         |
|. =++..          |
|o=++.            |
+-----------------+
```

## Authors
* [Pablo Villalobos](https://github.com/pablo-vs)
* [Carlos Bilbao](https://github.com/Zildj1an)
* [Ana Matesanz](https://github.com/anamatesanz)

## License
This project's source code is licensed under the GNU-GPL License - see the <a href="https://github.com/Zildj1an/SELEX/blob/master/LICENSE">LICENSE.md</a> file for details. The other parts of the project have the Creative Commons license, as stated in the competition guidelines.

