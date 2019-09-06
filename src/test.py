from opentrons import labware, instruments, modules, robot
from opentrons.data_storage import database
from time import sleep


sample     = labware.load('96-flat', slot = 3)
tiprack    = labware.load('opentrons-tiprack-300ul', slot=9)
tiprack_l  = labware.load('opentrons-tiprack-300ul', slot=5)

# [2] Pipettes

pipette_r = instruments.P50_Multi(mount = 'right', tip_racks=[tiprack])
pipette_l = instruments.P300_Single(mount='left', tip_racks=[tiprack_l])

pipette_l.transfer(100, sample.wells('A1'), sample.wells('A3'))
pipette_l.transfer(100, sample.wells('B1'), sample.wells('B3'))
pipette_l.transfer(100, sample.wells('C1'), sample.wells('C3'))

pipette_r.transfer(50, sample.wells('A3'), sample.wells('A4'))
pipette_r.transfer(50, sample.wells('A3'), sample.wells('A5'))
pipette_r.transfer(50, sample.wells('A1'), sample.wells('A6'))
                   
