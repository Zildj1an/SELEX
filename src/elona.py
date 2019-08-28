'''
 Elona Protocol (Elisa for aptamers)

 Coating -> Dyeing (optional) -> Elona

 Requires a custom module with ice for the antibody

'''

from opentrons import labware, instruments, modules, robot
from opentrons.data_storage import database
from time import sleep

metadata = {
   'protocolName' : 'ELONA',
   'description'  : 'Aptamer binding',
   'source'       : 'https://github.com/Zildj1an/SELEX'
}

# [1] Labware

database.delete_container('96-flat-1')

storage_name = 'Storage_Module'
if storage_name not in labware.list():
   Storage = labware.create(
      storage_name,
      grid = (10,1),
      spacing = (12.5,0),
      diameter = 9,
      depth  = 40,
      volume = 200000)

ninja_name = "NinjaTempDeck"
if ninja_name not in labware.list():
   labware.create(
      ninja_name,                        # Labware Name
      grid=(4, 4),                    # Amount of (columns, rows)
      spacing=(9, 9),                 # Distances (mm) between each (column, row)
      diameter=2,                     # Diameter (mm) of each well on the plate
      depth=20,                       # Depth (mm) of each well on the plate
      volume=50)

plate_name = "96-flat-1"
if plate_name not in labware.list():
   labware.create(
      plate_name,                        # Labware Name
      grid=(12, 8),                    # Amount of (columns, rows)
      spacing=(9, 9),                 # Distances (mm) between each (column, row)
      diameter=7,                     # Diameter (mm) of each well on the plate
      depth=10,                       # Depth (mm) of each well on the plate
      volume=50)

Storage          = labware.load(storage_name, slot = 5)
plate_samples    = labware.load('96-flat',       slot = 2)
plate_buffers    = labware.load('96-flat-1',     slot = 3)
trash_liquid     = labware.load('corning_384_wellplate_112ul_flat', slot = 1)
td_lab           = labware.load(ninja_name, slot=10)
Eppendorf        = labware.load('Eppendorf_Samples', slot = 4)
tiprack_l        = labware.load('opentrons-tiprack-300ul', slot=9)
tiprack_r        = labware.load('opentrons-tiprack-10ul', slot=6)
tiprack_r2       = labware.load('opentrons-tiprack-10ul', slot=11)
#tiprack_r3       = labware.load('opentrons-tiprack-10ul', slot=7)

# Note: tiprack_r is actually an 'opentrons-

# [2] Pipettes

pipette_l = instruments.P300_Single(mount = 'left', tip_racks=[tiprack_l])
pipette_r = instruments.P50_Multi(mount = 'right', tip_racks=[tiprack_r, tiprack_r2])#,tiprack_r3])

# Pipette flow rates: left and right, aspirate and dispense

flow_rate = {'a_l': 200, 'd_l': 200, 'a_r': 50, 'd_r': 50}

def addrow(well, num):
   # addrow('A1',1) -> 'B1'
   return chr(ord(well[0])+num) + well[1:]

# Right pipette will pick up tips in this order: E1,E2...E12,A1,A2....
# This way we can use a whole tiprack while only picking up four tips
# For this to work, you should always pick up tips with pipette_r.pick_up_tip
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

def storage_samples(where, vol, new_tip='once', module = Storage, safe_flow_rate=15, mix=False):

   # Where is an array: ['A1'] will always aspirate from that well. ['A1','A2','A3'] will transfer
   # from well A1 in module to first row in samples, A2 to second row, etc

   # safe_flow_rate sets the dispense rate

   if new_tip == 'once':
      pipette_r.pick_up_tip()

   times = vol // pipette_r.max_volume
   vol = vol % pipette_r.max_volume

   if len(where) < 3:
      # Support for different origins
      where *= 3

   for sample,origin in zip([f'A{i}' for i in range(1, 4)], where):

      # For every well in A1 - A3

      for x in range(1,times+1):

         if mix:
            pipette_r.set_flow_rate(aspirate=flow_rate['a_r'], dispense=flow_rate['d_r'])
            pipette_r.mix(3,25,module.wells(origin))
            pipette_r.set_flow_rate(aspirate = 50, dispense = safe_flow_rate)
         pipette_r.aspirate(pipette_r.max_volume,module.wells(origin))
         pipette_r.dispense(pipette_r.max_volume,plate_samples.wells(sample).bottom(3))
         pipette_r.blow_out(plate_samples.wells(sample))
         pipette_r.blow_out(plate_samples.wells(sample))

      if vol > 0:
         if mix:
            pipette_r.set_flow_rate(aspirate=flow_rate['a_r'], dispense=flow_rate['d_r'])
            pipette_r.mix(3,25,module.wells(origin))
            pipette_r.aspirate(vol,module.wells(origin))
         pipette_r.dispense(vol,plate_samples.wells(sample).bottom(3))
         pipette_r.blow_out(plate_samples.wells(sample))
         pipette_r.blow_out(plate_samples.wells(sample))

   if new_tip == 'once':
      pipette_r.drop_tip()

   pipette_r.set_flow_rate(aspirate=flow_rate['a_r'], dispense=flow_rate['d_r'])

def samples_trash(vol, new_tip='once', safe_flow_rate=15, downto=0):

   # safe_flow_rate sets the aspirate rate

   pipette_r.set_flow_rate(aspirate = safe_flow_rate, dispense = 50)
   times = vol // pipette_r.max_volume
   vol = vol % pipette_r.max_volume

   if new_tip == 'once':
      pipette_r.pick_up_tip()

   for sample in [f'A{i}' for i in range(1, 4)]:

      if new_tip == 'always':
         pipette_r.pick_up_tip()
      pipette_r.aspirate(pipette_r.max_volume,plate_samples.wells(sample).bottom(downto))
      pipette_r.dispense(pipette_r.max_volume,trash_liquid.wells(sample))
      pipette_r.blow_out(trash_liquid.wells(sample))
      pipette_r.touch_tip()

      if vol > 0:
         pipette_r.aspirate(vol,plate_samples.wells(sample).bottom(downto))
      pipette_r.dispense(vol,trash_liquid.wells(sample))
      pipette_r.blow_out(trash_liquid.wells(sample))
      pipette_r.touch_tip()

      if new_tip == 'always':
         pipette_r.drop_tip()

   if new_tip == 'once':
      pipette_r.drop_tip()

   pipette_r.set_flow_rate(aspirate=flow_rate['a_r'], dispense=flow_rate['d_r'])

def tween_wash():

   # (3) Lavado x3 con PBS 1x tween 0.1
   for x in range(1,4):
      storage_samples(['A5'],200)
      #samples_trash(200) MANUAL

      if not robot.is_simulating():
         robot.comment("Waiting...")
         robot._driver.turn_on_red_button_light()
         while not robot._driver.read_button():
            sleep(0.5)

         robot._driver.turn_on_blue_button_light()

      if x < 3:
         samples_trash(200, new_tip='once', downto = -5)

def robot_wait():
    if not robot.is_simulating():
       robot.comment("Waiting...")
       robot._driver.turn_on_red_button_light()
       while not robot._driver.read_button():
          sleep(0.5)

       robot._driver.turn_on_blue_button_light()

robot._driver.turn_on_rail_lights()
pipette_l.set_flow_rate(aspirate=flow_rate['a_l'], dispense=flow_rate['d_l'])

# (-2)
samples_trash(200, new_tip='once', downto = -5)
tween_wash()

# (1) 200ul of PBS 1x BSA 5% to plate
storage_samples(['A7','A8','A9'],200, module = plate_buffers, safe_flow_rate=15, mix=True)

# (2) Incubar 1h y estructurizar aptamers y retirar PBS - PAUSE (Hand made)
robot_wait()

# (3) Lavado con tween
tween_wash()

# (5) Add 100ul from each apt to the plates

for epp,dest in [('A1','A1'), ('A2','D1'), ('A2','D2'), ('A2','D3'), ('A3','A2'), ('A3','A3')]:
   # source, dest

   pipette_l.pick_up_tip()

   for pos in range(1,4):
      if '3' not in epp:
         # Don't mix aptamer buffer
         pipette_l.mix(3,50,Eppendorf.wells(epp))
      pipette_l.set_flow_rate(dispense=20)
      pipette_l.transfer(100,Eppendorf.wells(epp),plate_samples.wells(addrow(dest,pos-1)), new_tip='never', blow_out=True)
      pipette_l.set_flow_rate(dispense=200)

   pipette_l.drop_tip()

# Pausar para incubar 1h - PAUSE (Hand made)
robot_wait()

# (6) Lavado x3 con tween
tween_wash()

# (7) Eppendorf con anticuerpo A todos (en módulo térmico!)

for epp,dest in [('B1','A1'), ('B1','D1'), ('B1','A2'), ('B1','D3'), ('B2','A3'), ('B2','D2')]:

   pipette_l.pick_up_tip()

   for pos in range(1,4):
      if '3' not in epp:
         # Don't mix aptamer buffer
         pipette_l.mix(3,50,Eppendorf.wells(epp))
      pipette_l.set_flow_rate(dispense=20)
      pipette_l.transfer(100,Eppendorf.wells(epp),plate_samples.wells(addrow(dest,pos-1)), new_tip='never', blow_out=True)
      pipette_l.set_flow_rate(dispense=200)

   pipette_l.drop_tip()

# Pausar para incubar 1h - PAUSE (Hand made)
robot_wait()

# (8) Lavado x3 con PBS 1x tween 0.1
tween_wash()

# (9) Add 100ul of ABTS
storage_samples(['A10','A11','A12'],100, module = plate_buffers, safe_flow_rate=30)

robot.turn_off_rail_lights()

robot._driver.home()

