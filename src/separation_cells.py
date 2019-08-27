'''
Separate cells

'''
from opentrons import labware, instruments, modules, robot
from ninjapcr import NinjaPCR, NinjaTempDeck
from time import sleep

metadata = {
   'protocolName' : 'Separation of cells',
   'description'  : 'Separation of cells',
   'source'       : 'https://github.com/Zildj1an/SELEX'
}

plate_eppendorf = 'Eppendorf_Samples'
if plate_eppendorf not in labware.list():
   Eppendorf = labware.create(
      plate_eppendorf,
      grid = (8,4),
      spacing = (15,20),
      diameter = 10,
      depth  = 35,
      volume = 100)

magdeck          = modules.load('MagDeck', slot=4)
md_lab           = labware.load(magdeck_plate, slot=4, share=True)
tiprack          = labware.load('opentrons-tiprack-300ul', slot=6)
samples          = labware.load('Eppendorf_Samples', slot=8)

pipette_l        = instruments.P300_Single(mount='left', tip_racks=[tiprack])

