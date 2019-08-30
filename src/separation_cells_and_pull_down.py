'''
 Separate cells (Laura)
 AND pull down

'''
from opentrons import labware, instruments, modules, robot
from ninjapcr import NinjaPCR, NinjaTempDeck
from time import sleep

metadata = {
   'protocolName' : 'Separation of cells',
   'description'  : 'Separation of cells and pull down',
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

# FUNCTIONS ························································································

def robot_wait():

    if not robot.is_simulating():
       robot.comment("Waiting...")
       robot._driver.turn_on_red_button_light()
       while not robot._driver.read_button():
          sleep(0.5)

       robot._driver.turn_on_blue_button_light()

def wash(pos='D', ini=3,fin=4):

   amount = amount_init
   p1 = 1
   p2 = 2

   # "Lavados"
   for x in range(1,5):

      if x > 1:
         amount = 400
         p1 = 3
         p2 = 4

      # (4) Move amount from A1,A2 to B1,B2
      custom_pick(amount, md_lab.wells('A1'), samples.wells(pos + chr(p1)), blow_out=True)
      custom_pick(amount, md_lab.wells('A2'), samples.wells(pos + chr(p2)), blow_out=True)
      magdeck.disengage()

      if x < 4:

        # (5) Move 400ul of PBS to A1,A2
        pipette.delay(seconds=15)
        custom_pick(400, samples.wells('A'+chr(ini)), md_lab.wells('A1'),blow_out=True,mix_after=True)
        custom_pick(400, samples.wells('A'+chr(fin)), md_lab.wells('A2'),blow_out=True,mix_after=True)

        # (6) Engage 2 mins
        magdeck.engage()

def incubate(x):

  for x in range(1,x + 1):

     pipette.pick_up_tip()
     pipette.mix(3,100,md_lab.wells('A1'))
     pipette.drop_tip()
     pipette.pick_up_tip()
     pipette.mix(3,100,md_lab.wells('A2'))
     pipette.delay(seconds=15)
     pipette.drop_tip()

def custom_pick(quantity, from_w, to_w, blow_out=False, reuse_tip=False, mix_after=False):

     if not reuse_tip :
         pipette.pick_up_tip()
     pipette.transfer(quantity, from_w,to_w)
     if mix_after:
        pipette.mix(3,100,to_w)
     if blow_out:
        pipette.blow_out(to_w)
     if not reuse_tip:
        pipette_drop_tip()

# Labware

magdeck          = modules.load('MagDeck',           slot=7)
md_lab           = labware.load(magdeck_plate,       slot=7, share=True)
tiprack          = labware.load('opentrons-tiprack-300ul', slot=6)
samples          = labware.load('Eppendorf_Samples', slot=4)
samples2         = labware.load('96-flat', slot=5)
tempdeck         = NinjaTempDeck(slot=10, simulating = robot.is_simulating())
td_lab           = tempdeck.labware

# Pipette
pipette          = instruments.P300_Single(mount='left', tip_racks=[tiprack], trash_container=trash)

# START RUN ························································································

pipette.set_flow_rate(aspirate=15,dispense=15)
robot._driver.turn_on_rail_lights()
tempdeck.set_temp(temp=4)

# (-1) Move 100ul from A3 to each of the magdeck
pipette.mix(3,100,td_lab.wells('A1'))
custom_pick(100, td_lab.wells('A1'), md_lab.wells('A1'), blow_out=True)
pipette.mix(3,100,td_lab.wells('A1'))
custom_pick(100, td_lab.wells('A1'), md_lab.wells('A2'), blow_out=True)

# (0) Remove liquid beads
magdeck.engage()
pipette.delay(seconds=120)
pipette.pick_up_tip()
custom_pick(100, md_lab.wells('A1'), samples.wells('B1'),reuse_tip=False, blow_out=True)
custom_pick(100, md_lab.wells('A2'), samples.wells('B1'),reuse_tip=False, blow_out=True)
pipette.drop_tip()
magdeck.disengage()

# (1) Add 700 ul from A1,A2 to magdeck

pipette.pick_up_tip()
pipette.mix(3,100,samples.wells('A1'))
custom_pick(700, samples.wells('A1'), md_lab.wells('A1'),blow_out=True,reuse_tip=False)
pipette.drop_tip()

pipette.pick_up_tip()
pipette.mix(3,100,samples.wells('A2'))
custom_pick(700, samples.wells('A2'), md_lab.wells('A2'),blow_out=True,reuse_tip=False)
pipette.drop_tip()

# (2) 10 min incubate
incubate(10)

# (3) Engage 2 mins
magdeck.engage()
pipette.delay(seconds=120)

# (4,5,6) Wash I
wash()

# (7) Pull-down

custom_pick(700, samples.wells('B8'), md_lab.wells('A1'), blow_out=True)
custom_pick(700, samples.wells('B8'), md_lab.wells('A2'), blow_out=True)

# (8) Incubation and take pull-down out
incubate(20)
magdeck.engage()
pipette.delay(120)

custom_pick(700, md_lab.wells('A1'), samples.wells('C1'), blow_out=True)
custom_pick(700, md_lab.wells('A2'), samples.wells('C2'), blow_out=True)
magdeck.disengage()

# (9,10,11) Wash II
wash(pos='C',ini=5,fin=6)

# (12) Elution, move 100ul of elution buffer A6 to A1,A2
pipette.delay(seconds=20)
custom_pick(100, samples.wells('A7'), md_lab.wells('A1'),blow_out=True)
custom_pick(100, samples.wells('A7'), md_lab.wells('A2'),blow_out=True)
incubate(5)

# (13) Engage 1 mins
magdeck.engage()
pipette.delay(seconds=60)

# (14) Move 100ul from A1,A2 to C1,C2
custom_pick(100, md_lab.wells('A1'), samples.wells('D5'), blow_out=True)
custom_pick(100, md_lab.wells('A2'), samples.wells('D6'), blow_out=True)
magdeck.disengage()

# (15) Move 100ul from  A7 eppendorf to A1,A2
custom_pick(100, samples.wells('A8'), md_lab.wells('A1'),blow_out=True,mix_after=True)
custom_pick(100, samples.wells('A8'), md_lab.wells('A2'),blow_out=True,mix_after=True)

# (16) Traspaso

custom_pick(100, md_lab.wells('A1'), samples2.wells('G1'),blow_out=True)
custom_pick(100, md_lab.wells('A2'), samples2.wells('G2'),blow_out=True)

matrix = [('A1','A1'),('A2','A2'),('C1','F1'),('C2','F2'),('C3','D1'),('C4','D2'),('D1','B1'),('D2','B2'),('D3','C1'),('D4','C2'),('D5','E1'),('D6','E2')]

for orig,end in matrix:
        custom_pick(100,samples.wells(orig),samples2.wells(end),blow_out=True)

# (17) Dilution

end = 6

for pos in ['C','D','A','B','E','F','G']:

    pos1 = 1
    pos2 = 2

    if pos == 'G':
       end = 3

    for x in range(1,end):

       pipette.pick_up_tip()
       custom_pick(100,samples2.wells(pos+chr(pos1)),samples2.wells(pos + chr(pos1 + 2)),blow_out=True, reuse_tip=True,mix_after=True)
       pos1 = pos1 + 2
       pipette.drop_tip()

    for x in range(1,end):

       pipette.pick_up_tip()
       custom_pick(100,samples2.wells(pos+chr(pos2)),samples2.wells(pos + chr(pos2 + 2)),blow_out=True,reuse_tip=True,mix_after=True)
       pos2 = pos2 + 2
       pipette.drop_tip()

robot._driver.turn_off_rail_lights()

