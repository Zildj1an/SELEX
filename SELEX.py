"""
@author Carlos Bilbao, Pablo Villalobos
@date July 12th, 2019
@version 1

"""

from opentrons import labware, instruments, modules, robot
from subprocess import Popen
from time import sleep
import os, requests, logging

metadata = {
	'protocolName' : 'Selex',
	'author'       : 'Carlos Bilbao, Pablo Villalobos',
	'description'  : 'Selex protocol for evolving aptamers',
	'source'       : 'https://github.com/Zildj1an/SELEX'
}

# [0] Ninja-PCR API

URL_PCR = "http://ninjapcr.local/command"
URL_AUX = "http://thermaux.local/command"

# [1] Labware
# TODO: Check types.

pcr_name = 'Ninja-PCR'
if pcr_name not in labware.list():
    thermocicler = labware.create(
        pcr_name,                       # Labware Name
        grid=(4, 4),                    # Amount of (columns, rows)
        spacing=(9, 9),                 # Distances (mm) between each (column, row)
        diameter=2,                     # Diameter (mm) of each well on the plate
        depth=10,                       # Depth (mm) of each well on the plate
        volume=50)

thermic_name = 'Thermic_Module'
if thermic_name not in labware.list():
    thermic = labware.create(
        thermic_name,                   # Labware Name
        grid=(4, 4),                    # Amount of (columns, rows)
        spacing=(9, 9),                 # Distances (mm) between each (column, row)
        diameter=2,                     # Diameter (mm) of each well on the plate
        depth=10,                       # Depth (mm) of each well on the plate
        volume=50)

plate_samples    =   labware.load('96-flat',      slot ='11')  			    # Samples
tiprack          =   labware.load('tiprack-10ul', slot='6')	         	    # Tipracks
magnetic         =   modules.load('magdeck',      slot ='1')	                    # Magnetic Deck
plate_magnet     =   labware.load('96-flat',      slot ='1', share = True)	    # Magnetic Deck plate
thermocycler     =   labware.load(pcr_name,       slot ='10')			    # Ninja-PCR
thermic_module   =   labware.load(thermic_name,   slot ='3')			    # Auxiliar thermic module
trash            =   labware.load('trash-box',    slot = '12', share = True)        # Trash

# [2] Pipettes

pipette_l   = instruments.P50_Single(mount = 'left', tip_racks=[tiprack], trash_container = trash)
pipette_r   = instruments.P50_Multi(mount = 'right', tip_racks=[tiprack], trash_container = trash)

# [3] Commands

def execute_move(function):

        # When the robot starts moving light goes on and
        # button turns red
        robot._driver.turn_on_rail_lights()
        robot._driver.turn_on_red_button_light()
        cmd  = "ffplay -nodisp -autoexit /mnt/usbdrive/robot.mp3 &> /dev/null"
        cmd2 = "pkill ffplay"

        # Will play while door is opened
        while not robot._driver.read_window_switches():

               p = Popen(cmd,shell=True)

               while not robot._driver.read_window_switches() and p.poll() is None:
                      sleep(.1)
               if robot._driver.read_window_switches() and p.poll() is None:
                      os.system(cmd2)
        try:
           function()
        except:
           print("Error calling function " + function().__name__ + "\n")

        robot._driver.turn_off_rail_lights()
        robot._driver.turn_on_blue_button_light()

def samples_to_pcr():

        pipette_r.pick_up_tip()

        for x,y in [('E1','A1'),('E2','A2'),('E3','A3'),('E4','A4')]:

         	# Aspirate 4
                pipette_r.aspirate(50,plate_samples.wells(x))
	        # Dispense 4
                pipette_r.dispense(50,thermocycler.wells(y))

        pipette_r.drop_tip()

def samples_to_aux():

       pipette_r.pick_up_tip()

       for x in ['A1','A2','A3','A4']:

             pipette_r.aspirate(50,thermocycler.wells(x))
             pipette_r.dispense(50,thermic_module.wells(x))

       pipette_r.drop_tip()

def api_request(temp, URL):

         command = '(1[1500|' + temp + '|Final Hold|0])'
         PARAMS = {'s': 'ACGTC',
                   'c':'start',
                   'l': temp, 			# Ignored by aux therm
                   'p': command}
         r = requests.get(url = URL, params = PARAMS)
         print(r.json)

# [4] SELEX execution

logging.getLogger("opentrons").setLevel(logging.INFO)

# (1) Warming at 90 degrees for 600 seconds (PCR)

print("Applying heat to samples...\n")
#api_request('90',URL_PCR)
execute_move(samples_to_pcr)

# (2) Cooling at 4 degrees for 600 seconds (aux)

print("Moving samples to cool them...\n")
#api_request('4', URL_AUX)
# TODO cerrar la puerta
# TODO sleep 10 mins
sleep(1)
execute_move(samples_to_aux)

# (3)

#api_request(,URL_AUX) TODO a que temp?
#sleep(1 hour)

# (4) Magnentic separation

# The first time you wish to get read of the ones stuck to the
# non-modified e.coli
# moverlo a magdeck
# magnetic.engage()

# (5)

# (6)

# (7)

robot._driver.home()

