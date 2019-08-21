from opentrons import labware, instruments, modules, robot
from opentrons.data_storage import database
from time import sleep


trash_liquid     = labware.load('corning_384_wellplate_112ul_flat', slot = 4)
tiprack_l        = labware.load('opentrons-tiprack-300ul', slot=9)
tiprack_r        = labware.load('opentrons-tiprack-10ul', slot=6)

# [2] Pipettes

pipette_l = instruments.P300_Single(mount = 'left', tip_racks=[tiprack_l])
pipette_r = instruments.P50_Multi(mount = 'right')

multi_tip_loc = ['E',1]

def pick_up_multi():

   global multi_tip_loc
   
   pipette_r.pick_up_tip(location = tiprack_r.wells(''.join(map(str,multi_tip_loc))))
   
   if multi_tip_loc[1] == 12:
      if multi_tip_loc[0] == 'A':
         raise Exception("Multichannel out of tips")
      multi_tip_loc = ('A',1)

   else:
      multi_tip_loc[1] += 1


pipette_l.pick_up_tip()

pipette_l.aspirate(50, trash_liquid.wells('A1'))
pipette_l.dispense(50, trash_liquid.wells('A1'))


pipette_l.return_tip()
      
pick_up_multi()

pipette_r.aspirate(50, trash_liquid.wells('A1'))
pipette_r.dispense(50, trash_liquid.wells('A1'))

pipette_r.return_tip()
                   
