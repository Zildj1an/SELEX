# imports
from opentrons import labware, instruments, robot
from time import sleep

# metadata
metadata = {
    'protocolName': 'My Protocol',
    'author': 'Name <email@address.com>',
    'description': 'Simple protocol to get started using OT2',
}

# labware
if "eppendorf_rack" not in labware.list():
    labware.create(
        "eppendorf_rack",
        grid=(12,8),
        spacing=(9,9),
        diameter=7.5,
        depth=21,
        volume=50)

plate = labware.load('eppendorf_rack', '8')
tiprack = labware.load('opentrons-tiprack-300ul', '6')

# pipettes
pipette = instruments.P50_Multi(mount='right')

# commands
pipette.pick_up_tip(tiprack.wells('A12'), increment = 0.5)

pipette.move_to(plate.wells('A1').bottom())
pipette.aspirate(10)
pipette.move_to(plate.wells('A1').top(50))
if not robot.is_simulating():
    sleep(20)
pipette.return_tip()
