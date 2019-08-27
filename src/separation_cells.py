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
pipette.pick_up_tip()
pipette.transfer(500, samples.wells('A1'), md_lab.wells('A1'))
pipette_drop_tip()
pipette.pick_up_tip()
pipette.transfer(500, samples.wells('A2'), md_lab.wells('A2'))
pipette.drop_tip()

# (1) Move 150ul from A3 to each of the magdeck
pipette.pick_up_tip()
pipette.transfer(150, samples.wells('A3'), md_lab.wells('A1'))
pipette.drop_tip()
pipette.pick_up_tip()
pipette.transfer(150, samples.wells('A3'), md_lab.wells('A2'))
pipette.drop_tip()

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
    pipette.pick_up_tip()
    pipette.transfer(amount, md_lab.wells('A1'), samples.wells('B' + chr(p1)))
    pipette.drop_tip()

    pipette.pick_up_tip()
    pipette.transfer(amount, md_lab.wells('A2'), samples.wells('B' + chr(p2)))
    magdeck.disengage()
    pipette.drop_tip()

    if x < 4:

       # (5) Move 500ul of PBS to A1,A2
       pipette.delay(seconds=15)

       pipette.pick_up_tip()
       pipette.transfer(500, samples.wells('A4'), md_lab.wells('A1'))
       pipette.blow_out(md_lab.wells('A1'))
       pipette.drop_tip()

       pipette.pick_up_tip()
       pipette.transfer(500, samples.wells('A4'), md_lab.wells('A2'))
       pipette.blow_out(md_lab.wells('A2'))
       pipette.drop_tip()

       # (6) Engage 3 mins
       magdeck.engage()
       pipette.delay(seconds=180)

# (7) Move 100ul of elution buffer A5 to A1,A2
pipette.delay(seconds=20)

pipette.pick_up_tip()
pipette.transfer(100, samples.wells('A5'), md_lab.wells('A1'))
pipette.blow_out(md_lab.wells('A1'))
pipette_drop_tip()

pipette.pick_up_tip()
pipette.transfer(100, samples.wells('A5'), md_lab.wells('A2'))
pipette.blow_out(md_lab.wells('A2'))
pipette.drop_tip()

# (8) Engage 1.5 mins
magdeck.engage()
pipette.delay(seconds=90)

# (9) Move 100ul from A1,A2 to C1,C2
pipette.pick_up_tip()
pipette.transfer(100, md_lab.wells('A1'), samples.wells('C1'))
pipette.drop_tip()

pipette.pick_up_tip()
pipette.transfer(100, md_lab.wells('A2'), samples.wells('C2'))
magdeck.disengage()
pipette.drop_tip()

# (10) Move 100ul from  A6 eppendorf to A1,A2
pipette.pick_up_tip()
pipette.transfer(100, samples.wells('A6'), md_lab.wells('A1'))
pipette.blow_out(md_lab.wells('A1'))
pipette.drop_tip()

pipette.pick_up_tip()
pipette.transfer(100, samples.wells('A6'), md_lab.wells('A2'))
pipette.blow_out(md_lab.wells('A2'))
pipette.drop_tip()

# (11) Dilution
pipette.pick_up_tip()
pipette.transfer(100, md_lab.wells('A1'), samples.wells('D1'))
pipette.blow_out(samples.wells('D1'))
pipette.drop_tip()

pipette.pick_up_tip()
pipette.transfer(100, md_lab.wells('A2'), samples.wells('D2'))
pipette.blow_out(samples.wells('D2'))
pipette.drop_tip()

for pos in ['A','B','C','D']:

    pipette.pick_up_tip()
    pipette.transfer(100,samples.wells(pos+chr(1)),samples2.wells(pos + chr(1)))
    pipette.blow_out(samples2.wells(pos+chr(1)))
    pipette.transfer(100,samples.wells(pos+chr(2)),samples2.wells(pos + chr(2)))
    pipette.blow_out(samples2.wells(pos+chr(1)))
    pipette.blow_out(samples2.wells(pos+chr(2)))

for pos in ['C','D','A','B']:

    pos1 = 1
    pos2 = 2

    for x in range(1,4):

       pipette.transfer(100,samples2.wells(pos+chr(pos1)),samples2.wells(pos + chr(pos1 + 2)))
       pipette.transfer(100,samples2.wells(pos+chr(pos2)),samples2.wells(pos + chr(pos2 + 2)))
       pipette.blow_out(samples2.wells(pos + chr(pos1 + 2)))
       pipette.blow_out(samples2.wells(pos + chr(pos2 + 2)))
       pos1 = pos1 + 2
       pos2 = pos2 + 2

pipette.transfer(100,samples.wells('B3'),samples.wells('B5')
pipette.transfer(100,samples.wells('B4'),samples.wells('B6')
pipette.blow_out(samples.wells('B5'))
pipette.blow_out(samples.wells('B6'))
pipette.transfer(100,samples.wells('B5'),samples.wells('B7')
pipette.transfer(100,samples.wells('B6'),samples.wells('B8')
pipette.blow_out(samples.wells('B7'))
pipette.blow_out(samples.wells('B8'))
pipette.transfer(100,samples.wells('B7'),samples.wells('C3')
pipette.transfer(100,samples.wells('B8'),samples.wells('C4')
pipette.blow_out(samples.wells('C3'))
pipette.blow_out(samples.wells('C4'))
pipette.transfer(100,samples.wells('C3'),samples.wells('C5')
pipette.transfer(100,samples.wells('C4'),samples.wells('C6')
pipette.blow_out(samples.wells('C5'))
pipette.blow_out(samples.wells('C6'))


robot._driver.turn_off_rail_lights()

