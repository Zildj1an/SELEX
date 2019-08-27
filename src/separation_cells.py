'''
Separate cells (Laura)

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

def robot_wait():

    if not robot.is_simulating():
       robot.comment("Waiting...")
       robot._driver.turn_on_red_button_light()
       while not robot._driver.read_button():
          sleep(0.5)

       robot._driver.turn_on_blue_button_light()

def custom_pick(quantity, from_w, to_w, blow_out=False, reuse_tip=False):

     if not reuse_tip :
         pipette.pick_up_tip()
     pipette.transfer(quantity, from_w,to_w)
     if blow_out == True:
        pipette.blow_out(to_w)
     if not reuse_tip:
        pipette_drop_tip()

# Labware

magdeck          = modules.load('MagDeck', slot=4)
md_lab           = labware.load(magdeck_plate, slot=4, share=True)
tiprack          = labware.load('opentrons-tiprack-300ul', slot=6)
samples          = labware.load('Eppendorf_Samples', slot=8)
samples2         = labware.load('Eppendorf_Samples', slot=9)

# Pipette
pipette          = instruments.P300_Single(mount='left', tip_racks=[tiprack])

pipette.set_flow_rate(aspirate=15,dispense=15)
robot._driver.turn_on_rail_lights()

# (0) Add 500 ul from A1,A2 to magdeck
custom_pick(500, samples.wells('A1'), md_lab.wells('A1'))
custom_pick(500, samples.wells('A2'), md_lab.wells('A2'))

# (1) Move 150ul from A3 to each of the magdeck
custom_pick(150, samples.wells('A3'), md_lab.wells('A1'))
custom_pick(150, samples.wells('A3'), md_lab.wells('A2'))

# (2) 1h incubate
robot_wait()

# (3) Engage 3 mins
magdeck.engage()
pipette.delay(seconds=180)
amount = 650
p1 = 1
p2 = 2

for x in range(1,5):

    if x > 1:
      amount = 500
      p1 = 3
      p2 = 4

    # (4) Move 650 from A1,A2 to B1,B2
    custom_pick(amount, md_lab.wells('A1'), samples.wells('B' + chr(p1)))
    custom_pick(amount, md_lab.wells('A2'), samples.wells('B' + chr(p2)))
    magdeck.disengage()

    if x < 4:

       # (5) Move 500ul of PBS to A1,A2
       pipette.delay(seconds=15)
       custom_pick(500, samples.wells('A4'), md_lab.wells('A1'),blow_out=True)
       custom_pick(500, samples.wells('A4'), md_lab.wells('A2'),blow_out=True)

       # (6) Engage 3 mins
       magdeck.engage()
       pipette.delay(seconds=180)

# (7) Move 100ul of elution buffer A5 to A1,A2
pipette.delay(seconds=20)

custom_pick(100, samples.wells('A5'), md_lab.wells('A1'),blow_out=True)
custom_pick(100, samples.wells('A5'), md_lab.wells('A2'),blow_out=True)

# (8) Engage 1.5 mins
magdeck.engage()
pipette.delay(seconds=90)

# (9) Move 100ul from A1,A2 to C1,C2
custom_pick(100, md_lab.wells('A1'), samples.wells('C1'))
custom_pick(100, md_lab.wells('A2'), samples.wells('C2'))
magdeck.disengage()

# (10) Move 100ul from  A6 eppendorf to A1,A2
custom_pick(100, samples.wells('A6'), md_lab.wells('A1'),blow_out=True)
custom_pick(100, samples.wells('A6'), md_lab.wells('A2'),blow_out=True)

# (11) Dilution
custom_pick(100, md_lab.wells('A1'), samples.wells('D1'),blow_out=True)
custom_pick(100, md_lab.wells('A2'), samples.wells('D2'),blow_out=True)

for pos in ['A','B','C','D']:

    custom_pick(100,samples.wells(pos+chr(1)),samples2.wells(pos + chr(1)),blow_out=True)
    custom_pick(100,samples.wells(pos+chr(2)),samples2.wells(pos + chr(2)),blow_out=True)

for pos in ['C','D','A','B']:

    pos1 = 1
    pos2 = 2

    for x in range(1,4):

       pipette.pick_up_tip()
       custom_pick(100,samples2.wells(pos+chr(pos1)),samples2.wells(pos + chr(pos1 + 2)),blow_out=True, reuse_tip=True)
       pos1 = pos1 + 2
       pipette.drop_tip()

    for x in range(1,4):

       pipette.pick_up_tip()
       custom_pick(100,samples2.wells(pos+chr(pos2)),samples2.wells(pos + chr(pos2 + 2)),blow_out=True,reuse_tip=True)
       pos2 = pos2 + 2
       pipette.drop_tip()

# B3
pipette.pick_up_tip()

for x, y in [('B3','B5'),('B5,B7'),('B7,C3'),('C3,C5')]:
   custom_pick(100,samples.wells(x),samples.wells(y),blow_out=True,reuse_tip=True)

pipette.drop_tip()

# B4
pipette.pick_up_tip()

for x, y in [('B4','B6'),('B6,B8'),('B8,C4'),('C4,C6')]:
    custom_pick(100,samples.wells(x),samples.wells(y),blow_out=True,reuse_tip=True)

pipette.drop_tip()

robot._driver.turn_off_rail_lights()


