"""
@author Carlos Bilbao, Pablo Villalobos
@date July 12th, 2019
@version 1

"""

from opentrons import labware, instruments, modules, robot
from subprocess import Popen
from time import sleep
import os

metadata = {
	'protocolName' : 'Selex',
	'author'       : 'Carlos Bilbao, Pablo Villalobos',
	'description'  : 'Selex protocol for evolving aptamers',
	'source'       : '2019.igem.org/Team:MADRID_UCM/Landing'
}

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
thermocicler     =   labware.load(pcr_name,       slot ='10')			    # Ninja-PCR
thermic_module   =   labware.load(thermic_name,   slot ='3')			    # Auxiliar thermic module

# [2] Pipettes

pipette_l   = instruments.P50_Single(mount = 'left', tip_racks=[tiprack])
pipette_r   = instruments.P50_Multi(mount = 'right', tip_racks=[tiprack])

# [3] Commands

def init_move(function):

        # When the robot starts moving light goes on and
        # button turns red
        robot._driver.turn_on_rail_lights()
        robot._driver.turn_on_red_button_light()
        cmd  = "ffplay -nodisp -autoexit /root/robot.mp3"
        cmd2 = "pkill ffplay" 

        # Will play while door is opened
        while not robot._driver.read_window_switches():

               p = Popen(cmd,shell=True)
 
               while not robot._driver.read_window_switches() and p.poll() is None:
                      sleep(.1)
               if robot._driver.read_window_switches() and p.poll() is None:
                      os.system(cmd2)
       
        function()
    
        robot._driver.turn_off_rail_lights()
        robot._driver.turn_on_blue_button_light()

def samples_to_pcr():

        # Empezar a calentar a 90 grados (TODO)
        pipette_l.pick_up_tip()
        pipette_r.pick_up_tip()
        # pipette_r.aspirate(50, plate_samples.wells(x))
        # pipette_l.dispense(50,thermocicler.wells(8))
        # TODO basura en vez de devolver
        pipette_l.return_tip()
        pipette_r.return_tip()

def samples_to_aux():

       robot._driver.turn_on_rail_lights()
       pipette_l.pick_up_tip()
       # aspirar de pcr, dispensar en thermocicler
       pipette_l.return_tip()
       robot._driver.turn_off_rail_lights()

# [4] SELEX execution

# Warming at 90 degrees

print("Applying heat to sample...\n")
init_move(samples_to_pcr)

# Empezar a enfriar aux a 4 grados
# sleep(10 mins)

print("Moving samples to cool them...\n")
#init_move(samples_to_aux)

# ... (TODO)

robot._driver.home()


