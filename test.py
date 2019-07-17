# imports
from opentrons import labware, instruments

# metadata
metadata = {
    'protocolName': 'My Protocol',
    'author': 'Name <email@address.com>',
    'description': 'Simple protocol to get started using OT2',
}

# labware
plate = labware.load('96-flat', '2')
tiprack = labware.load('opentrons-tiprack-300ul', '1')

# pipettes
pipette = instruments.P50_Multi(mount='right', tip_racks=[tiprack])

# commands
pipette.transfer(100, plate.wells('A1'), plate.wells('B2'))

