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

plate_samples    =   labware.load('96-flat',      slot ='11')  			    # Samples
tiprack          =   labware.load('tiprack-10ul', slot='6')	         	    # Tipracks
magnetic         =   modules.load('magdeck',      slot ='1')	                    # Magnetic Deck
plate_magnet     =   labware.load('96-flat',      slot ='1', share = True)	    # Magnetic Deck plate
thermocicler     =   labware.load(pcr_name,       slot ='10')			    # Ninja-PCR
thermic_module   =   labware.load(thermic_name,   slot ='3')			    # Auxiliar thermic module

# [2] Pipettes

pipette_l = instruments.P50_Single(mount = 'left', tip_racks=[tiprack])
pipette_r = instruments.P50_Single(mount = 'right', tip_racks=[tiprack])

# [3] Commands
# TODO usar ambos pipettes

def samples_to_pcr():
        robot._driver.turn_on_rail_lights()
	# Empezar a calentar a 90 grados
        pipette_l.pick_up_tip()
        pipette_l.aspirate(50, plate_samples.wells('A1'))
        pipette_l.dispense(50, plate_samples.wells('B1'))
        pipette_l.return_tip()
        robot._driver.turn_off_rail_lights()

def samples_to_aux():
       robot._driver.turn_on_rail_lights()
       pipette_l.pick_up_tip()
       # aspirar de pcr, dispensar en thermocicler
       pipette_l.return_tip()
       robot._driver.turn_off_rail_lights()

# [4] SELEX execution

# Warming at 90 degrees

print("Applying heat to sample...\n")
samples_to_pcr()

# Empezar a enfriar aux a 4 grados
# sleep(10 mins)

samples_to_aux()

