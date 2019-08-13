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
#max_speed_per_axis = {'x': 600,'y': 400,'z': 125,'a': 125,'b': 40,'c': 40}
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
trash            =   labware.load('trash-box',    slot = '12', share = True)        # Trash
plate_samples    = labware.load('96-flat',       slot = '11')                       # Samples

# [2] Pipettes

pipette_l = instruments.P50_Single(mount = 'left', tip_racks=[tiprack], trash_container = trash)
pipette_l.set_flow_rate(aspirate = 50, dispense = 50)

volume_50 = 50000
ml_rate = 9/5000

def custom_transfer(pipette,quantity,pos1,pos2,A,B,depth=1):

   times = quantity // 50

   for i in range(1,times+1):
      pipette.aspirate(50,pos1.wells(A).bottom(depth))
      pipette.dispense(50,pos2.wells(B))
      pipette.blow_out(pos2.wells(B).top(-4))
      pipette.touch_tip()

   quantity = quantity - (times * 50)

   if quantity > 0:
      pipette.aspirate(quantity,pos1.wells(A).bottom(depth))
      pipette.dispense(quantity,pos2.wells(B))
      pipette.blow_out(pos2.wells(B).top(-4))

# [3] Execution

# Previous:
# Each Falcon has 1 ml shaked of PBS (Human part BEFORE Protocol)

# (1) Each Falcon to Eppendorfs:

robot._driver.turn_on_rail_lights()

falcon50 = 'A1'
val = 0

for falcon in ['C5']:

   custom_transfer(pipette_l,1200,Falcon,Eppendorf,falcon50,'A1',volume_50*ml_rate)
   volume_50 -= 1200

   custom_transfer(pipette_l,1350,Falcon,Eppendorf,falcon50,'A2',volume_50*ml_rate)
   volume_50 -= 1350

   custom_transfer(pipette_l,1450,Falcon,Eppendorf,falcon50,'A3',volume_50*ml_rate)
   volume_50 -= 1450

   custom_transfer(pipette_l,1470,Falcon,Eppendorf,falcon50,'A4',volume_50*ml_rate)
   volume_50 -= 1470
   
   custom_transfer(pipette_l,1350,Falcon,Eppendorf,falcon50,'A5',volume_50*ml_rate)
   volume_50 -= 1350

   custom_transfer(pipette_l,1350,Falcon,Eppendorf,falcon50,'B2',volume_50*ml_rate)
   volume_50 -= 1350



   pipette_l.transfer(300,Eppendorf.wells(falcon),Eppendorf.wells('A1'),new_tip='once', mix_before=(3,50), blow_out=True)

   pipette_l.transfer(150,Eppendorf.wells(falcon),Eppendorf.wells('A2'),new_tip='once', mix_before=(3,50), blow_out=True)
   
   pipette_l.transfer(50,Eppendorf.wells(falcon),Eppendorf.wells('A3'),new_tip='once', mix_before=(3,50), blow_out=True)

   pipette_l.transfer(30,Eppendorf.wells(falcon),Eppendorf.wells('A4'),new_tip='once', mix_before=(3,50), blow_out=True)

   pipette_l.transfer(150,Eppendorf.wells(falcon),Eppendorf.wells('B2'),new_tip='once', mix_before=(3,50), blow_out=True)


   pipette_l.transfer(150,Eppendorf.wells('B2'),Eppendorf.wells('A5'),new_tip='once',mix_before=(3,50))

   '''
   
   # 1st Eppendorf -> 750 ul of PBS + 750 ul of Falcon15
   pipette_l.pick_up_tip()
   custom_transfer(pipette_l,750,Falcon,Eppendorf,falcon50,chr(ord('A')+ val)+'1',volume_50*ml_rate)
   volume_50 -= 750
   pipette_l.drop_tip()
   pipette_l.pick_up_tip()
   # pipette_l.mix(3,50,Eppendorf.wells(falcon))
   pipette_l.transfer(750,Eppendorf.wells(falcon),Eppendorf.wells(chr(ord('A')+ val)+'1'),new_tip='never', mix_before=(3,50), blow_out=True)
   pipette_l.drop_tip()

   # 2nd Eppendorf -> 1200 ul of PBS + 300 ul of Falcon15
   pipette_l.pick_up_tip()
   custom_transfer(pipette_l,1200,Falcon,Eppendorf,falcon50,chr(ord('A')+ val)+'2',volume_50*ml_rate)
   volume_50 -= 1200
   pipette_l.drop_tip()
   pipette_l.pick_up_tip()
   #pipette_l.mix(3,50,Eppendorf.wells(falcon))
   pipette_l.transfer(300,Eppendorf.wells(falcon),Eppendorf.wells(chr(ord('A')+ val)+'2'),new_tip='never', mix_before=(3,50), blow_out=True)
   pipette_l.drop_tip()

   # 3rd Eppendorf -> 1350 ul of PBS + 150 ul of Falcon
   pipette_l.pick_up_tip()
   custom_transfer(pipette_l,1350,Falcon,Eppendorf,falcon50,chr(ord('A')+ val)+'3',volume_50*ml_rate)
   volume_50 -= 1350
   pipette_l.drop_tip()
   pipette_l.pick_up_tip()
   #pipette_l.mix(3,50,Eppendorf.wells(falcon))
   pipette_l.transfer(150,Eppendorf.wells(falcon),Eppendorf.wells(chr(ord('A')+ val)+'3'),new_tip='never', mix_before=(3,50), blow_out=True)
   pipette_l.drop_tip()

   # 3rd Eppendorf -> 1470 ul of PBS + 30 ul of Falcon
   pipette_l.pick_up_tip()
   custom_transfer(pipette_l,1470,Falcon,Eppendorf,falcon50,chr(ord('A')+ val)+'4',volume_50*ml_rate)
   volume_50 -= 1470
   pipette_l.drop_tip()
   pipette_l.pick_up_tip()
   #pipette_l.mix(3,50,Eppendorf.wells(falcon))
   pipette_l.transfer(30,Eppendorf.wells(falcon),Eppendorf.wells(chr(ord('A')+ val)+'4'),new_tip='never', mix_before=(3,50), blow_out=True)
   pipette_l.drop_tip()

   val += 1
   '''

   
for j in range(1,6):

   pipette_l.pick_up_tip()

   for i in range(1,7):
      
      pipette_l.transfer(200,Eppendorf.wells('A' + str(j)),plate_samples.wells(chr(ord('A')+j-1)+str(i)), new_tip='never', mix_before=(3,50), blow_out=True)

   pipette_l.drop_tip()


robot._driver.turn_off_rail_lights()
robot._driver.home()

