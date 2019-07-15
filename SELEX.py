"""
@author Carlos Bilbao, Pablo Villalobos
@date July 12th, 2019
@version 1

"""

from opentrons import labware, instruments, modules, robot
import time

metadata = {
	'protocolName' : 'Selex',
	'author' : 'Carlos Bilbao, Pablo Villalobos',
	'description' : 'Selex protocol for evolving aptamers',
	'source' : '2019.igem.org/Team:MADRID_UCM/Landing'
}

# [1] Labware
# TODO: Comprobar types, confirmar position, {thermic module, Ninja-PCR} sizes.

pcr_name = 'Ninja-PCR'
if pcr_name not in labware.list():
    thermocicler = labware.create(
        pcr_name,                       # Labware Name
        grid=(4, 4),                    # Amount of (columns, rows)
        spacing=(12, 12),               # Distances (mm) between each (column, row)
        diameter=5,                     # Diameter (mm) of each well on the plate
        depth=10,                       # Depth (mm) of each well on the plate
        volume=200)

thermic_name = 'Thermic_Module'
if thermic_name not in labware.list():
    thermic = labware.create(
        thermic_name,                   # Labware Name
        grid=(4, 4),                    # Amount of (columns, rows)
        spacing=(12, 12),               # Distances (mm) between each (column, row)
        diameter=5,                     # Diameter (mm) of each well on the plate
        depth=10,                       # Depth (mm) of each well on the plate
        volume=200)

plate_samples    =   labware.load('96-flat', slot ='11')			    # Samples
tiprack          =   labware.load('tiprack-10ul', slot='6')	         	    # Tipracks
magnetic         =   modules.load('magdeck',slot ='1')	         		    # Magnetic Deck
plate_magnet     =   labware.load('96-flat', slot ='1', share = True)		    # Magnetic Deck plate
thermocicler     =   labware.load(pcr_name,slot ='10')				    # Ninja-PCR
thermic_module   =   labware.load(thermic_name, slot ='3')			    # Auxiliar thermic module

# [2] Pipettes

pipette = instruments.P50_Single(mount = 'left')

# [3] Commands

# Ejemplo: pipette.transfer(100, plate.wells('A1'), plate.wells('B1'))

# TODO
def get_pipette_head():
	print("Getting pipette head...\n");
	for r in ["A1","B1","C1","D1"] :
		pipette.pick_up_tip(tiprack.wells(r))
		
# [4] SELEX execution

get_pipette_head()

# When done
while True:
        robot.turn_off_button_light()
        time.sleep(.5)
        robot.turn_on_button_light()
        time.sleep(.5)


