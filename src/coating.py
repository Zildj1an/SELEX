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

# TODO usar la multiple

from opentrons import labware, instruments, modules, robot
from opentrons.data_storage import database

metadata = {
   'protocolName' : 'Coating',
   'description'  : 'Coating of the samples',
   'source'       : 'https://github.com/Zildj1an/SELEX'
}

# [0] Our design for the three modules

max_speed_per_axis = {
    'x': 600, 'y': 500, 'z': 150, 'a': 150, 'b': 40, 'c': 40}
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
      spacing = (35,43), #TODO change
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

pipette_l.set_flow_rate(aspirate=50, dispense=100)

volume_50 = 50000

ml_rate = 9/5000

def custom_transfer(pipette,quantity,pos1,pos2,A,B,depth=1):
   
   times = quantity // 50
   
   

   for i in range(1,times+1):
      pipette.aspirate(50,pos1.wells(A).bottom(depth))
      pipette.dispense(50,pos2.wells(B))
      pipette.blow_out(pos2.wells(B).top(-4))

   quantity = quantity - (times * 50)

   if quantity > 0:
      pipette.aspirate(quantity,pos1.wells(A).bottom(depth))
      pipette.dispense(quantity,pos2.wells(B))
      pipette.blow_out(pos2.wells(B).top(-4))
      
# [3] Execution

# Previous:
# Each Falcon has 1 ml shaked of PBS (Human part BEFORE Protocol)

# (1) Each Falcon to Eppendorfs:

falcon50 = 'A1'
val = 0

for falcon in ['B5','C5','D5']:

   # 1st Eppendorf -> 400 ul of PBS + 400 ul of Falcon15
   pipette_l.pick_up_tip()
   custom_transfer(pipette_l,400,Falcon,Eppendorf,falcon50,chr(ord('A')+ val)+'1',volume_50*ml_rate)
   volume_50 -= 400
   pipette_l.drop_tip()
   pipette_l.pick_up_tip()
   # pipette_l.mix(3,50,Eppendorf.wells(falcon))
   # RESUSPENDER EN CADA ASPIRATE-DISPENSE
   pipette_l.transfer(400,Eppendorf.wells(falcon),Eppendorf.wells(chr(ord('A')+ val)+'1'),new_tip='never', mix_before=(3,50), blow_out=True)
   pipette_l.drop_tip()
   
   # 2nd Eppendorf -> 640 ul of PBS + 160 ul of Falcon15
   pipette_l.pick_up_tip()
   custom_transfer(pipette_l,640,Falcon,Eppendorf,falcon50,chr(ord('A')+ val)+'2',volume_50*ml_rate)
   volume_50 -= 640
   pipette_l.drop_tip()
   pipette_l.pick_up_tip()
   #pipette_l.mix(3,50,Eppendorf.wells(falcon))
   pipette_l.transfer(160,Eppendorf.wells(falcon),Eppendorf.wells(chr(ord('A')+ val)+'2'),new_tip='never', mix_before=(3,50), blow_out=True)
   pipette_l.drop_tip()
   
   # 3rd Eppendorf -> 720 ul of PBS + 80 ul of Falcon
   pipette_l.pick_up_tip()
   custom_transfer(pipette_l,720,Falcon,Eppendorf,falcon50,chr(ord('A')+ val)+'3',volume_50*ml_rate)
   volume_50 -= 720
   pipette_l.drop_tip()
   pipette_l.pick_up_tip()
   #pipette_l.mix(3,50,Eppendorf.wells(falcon))
   #custom_transfer(pipette_l,80,Eppendorf,Eppendorf,falcon,chr(ord('A')+ val)+'3')
   pipette_l.transfer(80,Eppendorf.wells(falcon),Eppendorf.wells(chr(ord('A')+ val)+'3'),new_tip='never', mix_before=(3,50), blow_out=True)
   pipette_l.drop_tip()
   
   # 3rd Eppendorf -> 784 ul of PBS + 16 ul of Falcon
   pipette_l.pick_up_tip()
   custom_transfer(pipette_l,784,Falcon,Eppendorf,falcon50,chr(ord('A')+ val)+'4',volume_50*ml_rate)
   volume_50 -= 784
   pipette_l.drop_tip()
   pipette_l.pick_up_tip()
   #pipette_l.mix(3,50,Eppendorf.wells(falcon))
   #custom_transfer(pipette_l,16,Eppendorf,Eppendorf,falcon,chr(ord('A')+ val)+'4')
   pipette_l.transfer(16,Eppendorf.wells(falcon),Eppendorf.wells(chr(ord('A')+ val)+'4'),new_tip='never', mix_before=(3,50), blow_out=True)
   pipette_l.drop_tip()
   
   val += 1



   
for pos in ['A','B','C']:
      
   init = 1
   end = 6
   row = 'A'
      
   if pos == 'B':
      init = 7
      end  = 12

   if pos == 'C':
      row = 'E'
      
   for j in range(1,5):

      pipette_l.pick_up_tip()
      
      for i in range(init,end+1):

         pipette_l.transfer(100,Eppendorf.wells(pos + str(j)),plate_samples.wells(chr(ord(row)+j-1)+str(i)), new_tip='never', mix_before=(3,50), blow_out=True)
               
      pipette_l.drop_tip()
               


robot._driver.turn_off_rail_lights()
robot._driver.home()


