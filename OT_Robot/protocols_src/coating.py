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
   'protocolName' : 'Coating',
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
      depth  = 35,
      volume = 100)

# [1] Labware

Falcon           = labware.load(plate_falcon,    slot = '1')
Eppendorf        = labware.load(plate_eppendorf, slot = '5')
tiprack          = labware.load('opentrons-tiprack-300ul',  slot = '6')
plate_samples    = labware.load('96-flat',       slot = '3')                      # Samples

# [2] Pipettes

pipette_l = instruments.P300_Single(mount = 'left', tip_racks=[tiprack])

# Initial volume in the Falcon50 in ul
volume_50 = 30000
# Rate of conversion from ul to distance from the bottom of the well
ml_rate = 9/5000

def addrow(well, num):
   # addrow('A1',1) -> 'B1'
   return chr(ord(well[0])+num) + well[1:]

def custom_transfer(pipette,quantity,pos1,pos2,A,B,depth=1,new_tip='once', mix=False):

   times = quantity // pipette.max_volume

   if new_tip == 'once':
      pipette.pick_up_tip()

   for i in range(1,times+1):
      if new_tip == 'always':
         pipette.pick_up_tip()
      if mix:
         pipette.set_flow_rate(aspirate = 300, dispense = 300)
         pipette.mix(3,50,pos1.wells(A).bottom(depth))
         pipette.set_flow_rate(aspirate = 50, dispense = 50)
      pipette.aspirate(pipette.max_volume,pos1.wells(A).bottom(depth))
      pipette.dispense(pipette.max_volume,pos2.wells(B))
      pipette.blow_out(pos2.wells(B).top(-4))
      pipette.touch_tip()
      if new_tip == 'always':
         pipette.drop_tip()

   quantity = quantity % pipette.max_volume

   if quantity > 0:
      if new_tip == 'always':
         pipette.pick_up_tip()
      if mix:
         pipette.set_flow_rate(aspirate = 300, dispense = 300)
         pipette.mix(3,50,pos1.wells(A).bottom(depth))
         pipette.set_flow_rate(aspirate = 50, dispense = 50)
      pipette.aspirate(quantity,pos1.wells(A).bottom(depth))
      pipette.dispense(quantity,pos2.wells(B))
      pipette.blow_out(pos2.wells(B).top(-4))
      pipette.touch_tip()
      if new_tip == 'always':
         pipette.drop_tip()

   if new_tip == 'once':
      pipette.drop_tip()

# [3] Execution

# Previous:
# Each Falcon has 1 ml shaked of PBS (Human part BEFORE Protocol)

# (1) Each Falcon to Eppendorfs:

robot._driver.turn_on_rail_lights()

falcon50 = 'A1'
val      = 0
falcon   = 'C4'


pipette_l.set_flow_rate(aspirate = 300, dispense = 300)

pipette_l.pick_up_tip()
custom_transfer(pipette_l,1500,Falcon,Eppendorf,falcon50,'A1',volume_50*ml_rate, new_tip='never')
volume_50 -= 1500
pipette_l.drop_tip()


custom_transfer(pipette_l, 500, Eppendorf, Eppendorf, falcon, 'A1' , new_tip='once', mix=True)


matrix = [('A1', 'A6'),('A1', 'D6'),('A1', 'D7')]

# TODO, mix once briskly at the beginning

pipette_l.pick_up_tip()

for source, dest in matrix: 

   for i in range(1,4):
   
      pipette_l.transfer(200,Eppendorf.wells(source),plate_samples.wells(addrow(dest,i-1)), new_tip='never', mix_before=(3,50), blow_out=True)

pipette_l.drop_tip()


robot._driver.turn_off_rail_lights()
robot._driver.home()

