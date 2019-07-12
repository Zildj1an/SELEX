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
# TODO: Comprobar types, confirmar posición, thermic module, Ninja-PCR.

plate_name = 'Ninja-PCR'
if plate_name not in labware.list():
    custom_plate = labware.create(
        plate_name,                     # Labware Name
        grid=(4, 4),                    # Amount of (columns, rows)
        spacing=(12, 12),               # Distances (mm) between each (column, row)
        diameter=5,                     # Diameter (mm) of each well on the plate
        depth=10,                       # Depth (mm) of each well on the plate
        volume=200)

plate_samples    =   labware.load('96-flat', '11')				    # Samples
tiprack          =   labware.load('opentrons-tiprack-10ul', '8')		    # Tipracks
magnetic         =   modules.load('magdeck','1')				    # Magnetic Deck
plate_magnet     =   labware.load('96-flat', '1', share = True)			    # Magnetic Deck plate
thermocicler     =   modules.load('Ninja-PCR','10')				    # Ninja-PCR
thermic_module   =   modules.load()						    # Auxiliar thermic module

# [2] Pipettes
# TODO:

pipette = instruments.P50_Single(mount = 'left', tip_racks = [tiprack])

# [3] Commands
#TODO:

# Ejemplo: pipette.trasnfer(100, plate.wells('A1'), plate.wells('B1'))

# When done
while true:
        robot._driver.turn_off_button_light()
	time.sleep(.500)
        robot._driver.turn_on_button_light()




