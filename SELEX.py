"""
@author Carlos Bilbao, Pablo Villalobos
@date July 12th, 2019
@version 1

"""

from opentrons import labware, instruments, modules

metadata = {
	'protocolName' : 'Selex',
	'author' : 'Carlos Bilbao, Pablo Villalobos',
	'description' : 'Selex protocol for evolving aptamers',
	'source' : '2019.igem.org/Team:MADRID_UCM/Landing'
}


# [1] Labware
# TODO: Comprobar types, confirmar posición.

plate_samples    =   labware.load('96-flat', '11')			# Samples
tiprack          =   labware.load('tiprack-200ul', '8')                 # Tipracks
magnetic         =   modules.load('magdeck','1')			# Magnetic Deck
plate_magnet     =   labware.load('96-flat', '1', share = True)		# Magnetic Deck plate
thermocicler     =   modules.load()					# Ninja-PCR
thermic_module   =   modules.load()					# Auxiliar thermic module

# [2] Pipettes
# TODO:

# [3] Commands
#TODO:
