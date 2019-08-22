# OT-2 Robot DNA-SELEX Protocol

![version](https://img.shields.io/badge/version-1-blue.svg?cacheSeconds=2592000) [![Website shields.io](https://img.shields.io/website-up-down-green-red/http/shields.io.svg)](https://2019.igem.org/Team:MADRID_UCM/Landing)
[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](http://perso.crans.org/besson/LICENSE.html)

This is the biotechnological protocol for obtaining trained libraries of aptamer molecules automated with the Opentrons OT-2 robot. This protocol is a part of our contribution to the 2019 iGEM international biotechnology competition. We also did an **Artificial Intelligence algorithm** to predict the optimal DNA molecule shapes (more info beow). For the thermocycler we built the Ninja-PCR. More information about the entire project can be found in our <a href = "https://2019.igem.org/Team:MADRID_UCM/Landing">website</a>. The small-sized thermal cycler is controlled via motherboard Ninja-PCR Arduino-alike, as shown above, manually welded, whose code is in NinjaPCR [folder](https://github.com/Zildj1an/SELEX/tree/master/NinjaPCR). You can update a new binary since ESP8266 SystemOnChip includes the TCP/IP stack.

<img src="https://github.com/Zildj1an/SELEX/blob/master/img/robot.jpg" alt="" width="350"/> <img src="https://github.com/Zildj1an/SELEX/blob/master/img/ninja.png" alt="" width="445"/>

## The SELEX Process
Aptamers are a cutting-edge technology that is revolutionizing biotechnology, from biosensing to synthetic biology. Aptamers are single-strand DNA molecules that hold nature’s most important information: our genetic code.But instead of using DNA for carrying information, our aptamers depend on DNA’s 3-dimensional shape. We genetically engineer this shape to take hold of and mesh with our target molecule. DNA’s unique role in nature gives aptamers amazing characteristics, making them robust, stable, and cheap to produce. 

<p align="center"><img src="https://github.com/Zildj1an/SELEX/blob/master/img/aptameros.png" alt="" width="400"/></p>

_The SELEX process_

## Installation and Usage

You can clone this repo or download the zip. Make sure all the dependencies are covered. First line is for installation of pip at most Linux distributions.

```
$ sudo apt install python-pip || pacman -S python-pip
$ sudo pip install opentrons subprocess time os
```
The robot uses the audio robot.mp3 and gets it from Robot Raspberry's /mnt/usbdrive/ (put it there or edit the location).
You can load the protocol in the Opentrons application, available <a href = "https://opentrons.com/ot-app">here</a>.

## Artificial Intelligence Algorithm

Repository currently location: https://github.com/anamatesanz/Nemesis_AEGIS/
The main contributor and person in charge of this algorithm was [Ana Matesaz](https://github.com/anamatesanz). It is a Generative adversarial network.


## Authors
* [Pablo Villalobos](https://github.com/pablo-vs)
* [Carlos Bilbao](https://github.com/Zildj1an)

## License
This project's source code is licensed under the GNU-GPL License - see the <a href="https://github.com/Zildj1an/SELEX/blob/master/LICENSE">LICENSE.md</a> file for details. The other parts of the project have the Creative Commons license, as stated in the competition guidelines.

