'''
#####################################################
#  Coating of the samples.                          #
#  It is required:                                  #
#  * Three Falcon (different concentrations).       #
#  * One Falcon.                                    #
#  * Eppendorf plates.                              #
#  We printed our own custom modules.               #
#  Team: MADRID_UCM                                 #
#####################################################
'''

from opentrons import labware, instruments, modules, robot
from opentrons.data_storage import database

metadata = {
   'protocolName' : 'Coating_TEST',
   'description'  : 'Coating of the samples',
   'source'       : 'https://github.com/Zildj1an/SELEX'
}

# [0] Our design for the three modules

# X,Y,Z,A speeds for lateral,front and vertical motion for left and right
# B,C plunger speed for motor
max_speed_per_axis = {'x': 600,'y': 400,'z': 125,'a': 125,'b': 40,'c': 40}
robot.head_speed(**max_speed_per_axis)
'''
database.delete_container('Falcon_Samples')
database.delete_container('Eppendorf_Samples')
'''
plate_falcon = 'Falcon_Samples'
if plate_falcon not in labware.list():
   Falcon = labware.create(
      plate_falcon,
      grid = (3,2),
      spacing = (35,43),
      diameter = 10,
      depth  = 110,
      volume = 800)

plate_eppendorf = 'Eppendorf_Samples'
if plate_eppendorf not in labware.list():
   Eppendorf = labware.create(
      plate_eppendorf,
      grid = (8,4),
      spacing = (15,20),
      diameter = 10,
      depth  = 39,
      volume = 100)

# [1] Labware

Falcon           = labware.load(plate_falcon,    slot = '2')
Eppendorf        = labware.load(plate_eppendorf, slot = '5')
tiprack          = labware.load('tiprack-10ul',  slot = '6')
trash            = labware.load('trash-box',     slot = '12', share = True)
plate_samples    = labware.load('96-flat',       slot = '11')                       # Samples

# [2] Pipettes

pipette_l = instruments.P50_Single(mount = 'left', tip_racks=[tiprack], trash_container = trash)
pipette_l.set_flow_rate(aspirate = 50, dispense = 100)

depth = 30000*9/5000

robot._driver.turn_on_rail_lights()
pipette_l.pick_up_tip()
pipette_l.aspirate(50,Falcon.wells('A1').bottom(depth))
pipette_l.dispense(50,Eppendorf.wells('D2'))
pipette_l.aspirate(50,Falcon.wells('A1').bottom(depth))
pipette_l.dispense(50,Eppendorf.wells('D2'))
pipette_l.drop_tip()
robot._driver.turn_off_rail_lights()
