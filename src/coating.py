'''
#####################################################
#  Coating of the samples.                          #
#  It is required:                                  #
#  * Three Falcon15 (different concentrations).     #
#  * One Falcon50.                                  #
#  * Eppendorf plates.                              #
#  We printed our own custom modules.               #
#  Team: MADRID_UCM                                 #
#####################################################
'''

# TODO: Usar las multiples de cuatro en cuatro o seis en seis

from opentrons import labware, instruments, modules, robot

metadata = {
       'protocolName' : 'Coating',
       'description'  : 'Coating of the samples',
       'source'       : 'https://github.com/Zildj1an/SELEX'
}

# [0] Our design for the three modules

plate_falcon15 = 'Falcon_Samples15'
if plate_falcon15 not in labware.list():
   Falcon = labware.create(
      plate_falcon15,
      grid = (8,4),
      spacing = (1,2),
      diameter = 1,
      depth  = 2,
      volume = 50)

plate_falcon50 = 'Falcon_Samples50'
if plate_falcon50 not in labware.list():
   Falcon = labware.create(
      plate_falcon50,
      grid = (8,4),
      spacing = (1,2),
      diameter = 1,
      depth  = 2,
      volume = 50)

plate_eppendorf = 'Eppendorf_Samples'
if plate_falcon15 not in labware.list():
   Falcon = labware.create(
      plate_eppendorf,
      grid = (8,4),
      spacing = (1,2),
      diameter = 1,
      depth  = 2,
      volume = 50)

# [1] Labware

Falcon15         = labware.load(plate_falcon15,  slot = '5')
Falcon50         = labware.load(plate_falcon50,  slot = '6')
Eppendorf        = labware.load(plate_eppendorf, slot = '7')
tiprack          = labware.load('tiprack-10ul',  slot = '8')
trash            = labware.load('trash-box',     slot = '12', share = True)
plate_samples    = labware.load('96-flat',     slot ='11')                       # Samples

# [2] Pipettes

pipette_l = instruments.P50_Single(mount = 'left', tip_racks=[tiprack], trash_container = trash)

# [3] Execution

# (1)
# Dispense PBS 5 mili l to each Falcon15 from the Falcon50
# Done by human

robot._driver.turn_on_rail_lights()

# (2)
# We need to shake the samples
# Idea: Aspirate and dispense it all

pippete_l.pick_up_tip()
pipette_l.transfer(15,Falcon15.wells('A1'),Falcon15.wells('A1'))
pipette_l.drop_tip()
pippete_l.pick_up_tip()
pipette_l.transfer(15,Falcon15.wells('B1'),Falcon15.wells('B1'))
pipette_l.drop_tip()
pippete_l.pick_up_tip()
pipette_l.transfer(15,Falcon15.wells('C1'),Falcon15.wells('C1'))
pipette_l.drop_tip()

# (3) TODO boton bien shakeado sino repite

# (4) Each Falcon15 to Eppendorfs:

for falcon in ['A1','B1','C1']:

    # 1st Eppendorf -> 400 ul of PBS + 400 ul of Falcon15
    pipette_l.pick_up_tip()
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('A1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('A1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('A1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('A1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('A1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('A1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('A1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('A1'))
    pipette_l.drop_tip()
    pipette_l.pick_up_tip()
    pipette_l.transfer(50,Falcon15.wells(falcon),Eppendorf.wells('A1'))
    pipette_l.transfer(50,Falcon15.wells(falcon),Eppendorf.wells('A1'))
    pipette_l.transfer(50,Falcon15.wells(falcon),Eppendorf.wells('A1'))
    pipette_l.transfer(50,Falcon15.wells(falcon),Eppendorf.wells('A1'))
    pipette_l.transfer(50,Falcon15.wells(falcon),Eppendorf.wells('A1'))
    pipette_l.transfer(50,Falcon15.wells(falcon),Eppendorf.wells('A1'))
    pipette_l.transfer(50,Falcon15.wells(falcon),Eppendorf.wells('A1'))
    pipette_l.transfer(50,Falcon15.wells(falcon),Eppendorf.wells('A1'))
    pipette_l.drop_tip()

    # 2nd Eppendorf -> 640 ul of PBS + 160 ul of Falcon15
    pipette_l.pick_up_tip()
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('B1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('B1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('B1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('B1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('B1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('B1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('B1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('B1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('B1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('B1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('B1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('B1'))
    pipette_l.transfer(40,Falcon50.wells(falcon),Eppendorf.wells('B1'))
    pipette_l.drop_tip()
    pipette_l.pick_up_tip()
    pipette_l.transfer(50,Falcon15.wells(falcon),Eppendorf.wells('B1'))
    pipette_l.transfer(50,Falcon15.wells(falcon),Eppendorf.wells('B1'))
    pipette_l.transfer(60,Falcon15.wells(falcon),Eppendorf.wells('B1'))
    pipette_l.drop_tip()

    # 3rd Eppendorf -> 720 ul of PBS + 60 ul of Falcon15
    pipette_l.pick_up_tip()
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('C1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('C1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('C1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('C1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('C1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('C1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('C1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('C1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('C1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('C1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('C1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('C1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('C1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('C1'))
    pipette_l.transfer(20,Falcon50.wells(falcon),Eppendorf.wells('C1'))
    pipette_l.drop_tip()
    pipette_l.pick_up_tip()
    pipette_l.transfer(50,Falcon15.wells(falcon),Eppendorf.wells('C1'))
    pipette_l.transfer(10,Falcon15.wells(falcon),Eppendorf.wells('C1'))
    pipette_l.drop_tip()

    # 3rd Eppendorf -> 784 ul of PBS + 16 ul of Falcon15
    pipette_l.pick_up_tip()
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('D1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('D1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('D1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('D1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('D1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('D1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('D1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('D1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('D1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('D1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('D1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('D1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('D1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('D1'))
    pipette_l.transfer(50,Falcon50.wells(falcon),Eppendorf.wells('D1'))
    pipette_l.transfer(34,Falcon50.wells(falcon),Eppendorf.wells('D1'))
    pipette_l.drop_tip()
    pipette_l.pick_up_tip()
    pipette_l.transfer(16,Falcon15.wells(falcon),Eppendorf.wells('D1'))
    pipette_l.drop_tip()

    if falcon == 'A1' or falcon == 'C1':

          if falcon == 'A1':
                 init = 1
          else:
              init = 5

          # (5) Eppendorf to samples according to the matrix
          for pos in ['A','B','C','D']:
             pipette_l.pick_up_tip()
             for i in range(init,6):
                 pipette_l.transfer(50,Eppendorf.wells(falcon),plate_samples.wells(pos + str(i)))
                 pipette_l.transfer(50,Eppendorf.wells(falcon),plate_samples.wells(pos + str(i)))
             pipette_l.drop_tip()
    else:
           # (5) Eppendorf to samples according to the matrix
          for pos in ['A','B','C','D']:
             pipette_l.pick_up_tip()
             for i in range(7,13):
               pipette_l.transfer(50,Eppendorf.wells('D1'),plate_samples.wells(pos + str(i)))
               pipette_l.transfer(50,Eppendorf.wells('D1'),plate_samples.wells(pos + str(i)))
             pipette_l.drop_tip()

robot._driver.turn_off_rail_lights()
robot._driver.home()


