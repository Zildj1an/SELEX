'''
 Elona Protocol (Elisa for aptamers)

 Coating -> Dyeing (optional) -> Elona

 Requires a custom module with ice for the antibody

'''

from opentrons import labware, instruments, modules, robot
from opentrons.util.vector import Vector
from opentrons.drivers.rpi_drivers.gpio import set_button_light
from time import sleep, monotonic, perf_counter
import logging

metadata = {
   'protocolName' : 'ELONA',
   'description'  : 'Aptamer binding',
   'author'       : 'Carlos Bilbao, Pablo Villalobos',
   'source'       : 'https://github.com/Zildj1an/SELEX'
}

logging.basicConfig(filename='/root/elona')
log = logging.getLogger('elona')

# [1] Labware


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
      diameter=3,                     # Diameter (mm) of each well on the plate
      depth=10,                       # Depth (mm) of each well on the plate
      volume=50)

Storage          = labware.load(storage_name, slot = 2)
plate_samples    = labware.load('96-flat-1',       slot = 3)
plate_buffers    = labware.load('96-flat',     slot = 6)
td_lab           = labware.load(ninja_name, slot=1)
Eppendorf        = labware.load('Eppendorf_Samples', slot = 4)
tiprack_l        = labware.load('opentrons-tiprack-300ul', slot=9)
tiprack_r        = labware.load('opentrons-tiprack-300ul', slot=5)
# Note: tiprack_r is actually an 'opentrons-tiprack-300ul', but its name must be
# different than tiprack_l's to prevent calibration issues

# Use the regular trash as trash_liquid, but displace the pipette to avoid collisions
trash = robot.fixed_trash().top()
trash_liquid = trash

# [2] Pipettes
pipette_l = instruments.P300_Single(mount = 'left', tip_racks=[tiprack_l])
pipette_r = instruments.P50_Multi(mount = 'right', tip_racks=[tiprack_r])#, tiprack_r2,tiprack_r3, tiprack_r4])

# Pipette flow rates: left and right, aspirate and dispense
flow_rate = {'a_l': 300, 'd_l': 300, 'a_r': 100, 'd_r': 100}

max_speed_per_axis = {'x': 600,'y': 400,'z': 125,'a': 125,'b': 40,'c': 40}
robot.head_speed(**max_speed_per_axis)


def robot_wait_tiprack():

    if not robot.is_simulating():
       robot.comment("Waiting...")
       set_button_light(blue=True, red=True, green=True)
       while not robot._driver.read_button():
          sleep(0.5)

       robot._driver.turn_on_blue_button_light()


def custom_pick_up_tip(*args, **kwargs):
   # Attemp to pick up tip, if there are no more tips wait until the user presses the button
   # and pick again from the beginning.
   try:
      return pipette_r.pick_up_tip(*args, **kwargs)
   except:
      robot_wait_tiprack()
      pipette_r.reset()
      return pipette_r.pick_up_tip(*args, **kwargs)

def addrow(well, num):
   # addrow('A1',1) -> 'B1'
   return chr(ord(well[0])+num) + well[1:]

# Right pipette will pick up tips in this order: E1,E2...E12,A1,A2....
# This way we can use a whole tiprack while only picking up four tips
# For this to work, you should always pick up tips with pick_up_multi
multi_tip_loc = ['E',1]

def pick_up_multi():

   global multi_tip_loc

   custom_pick_up_tip(location = tiprack_r.wells(''.join(map(str,multi_tip_loc))))

   if multi_tip_loc[1] == 12:
      if multi_tip_loc[0] == 'A':
         raise Exception("Multichannel out of tips")
      multi_tip_loc = ('A',1)

   else:
      multi_tip_loc[1] += 1

def storage_samples(where, vol, new_tip='once', module = Storage, safe_flow_rate=15, mix=False, measure_time=True, downto=5):

   # Where is an array: ['A1'] will always aspirate from that well. ['A1','A2','A3'] will transfer
   # from well A1 in module to first col in samples, A2 to second col, etc

   # safe_flow_rate sets the dispense rate

   if new_tip == 'once':
      custom_pick_up_tip()

   times = vol // pipette_r.max_volume
   vol = vol % pipette_r.max_volume

   if len(where) < 9:
      # Support for different origins
      where *= 9

   first_dispense=True
   start_time=0
   
   for sample,origin in zip([f'A{i}' for i in range(1, 10)], where):

      # For every well in A1 - A3

      for x in range(1,times+1):

         if mix:
            pipette_r.set_flow_rate(aspirate=flow_rate['a_r'], dispense=flow_rate['d_r'])
            pipette_r.mix(3,25,module.wells(origin))
            pipette_r.set_flow_rate(aspirate = 50, dispense = safe_flow_rate)
         pipette_r.aspirate(pipette_r.max_volume,module.wells(origin).bottom())
         pipette_r.dispense(pipette_r.max_volume,plate_samples.wells(sample).bottom(downto))
         if measure_time and not robot.is_simulating:
       	    if first_dispense:
               start_time = monotonic()
               first_dispense = False
            end_time = monotonic()
            log.warning(f'Dispensed from {module.get_name()}:{origin} to {sample} at T={end_time-start_time}')
         pipette_r.blow_out(plate_samples.wells(sample).bottom(downto))

      if vol > 0:
         if mix:
            pipette_r.set_flow_rate(aspirate=flow_rate['a_r'], dispense=flow_rate['d_r'])
            pipette_r.mix(3,25,module.wells(origin))
            pipette_r.set_flow_rate(aspirate = 50, dispense = safe_flow_rate)
         pipette_r.aspirate(vol,module.wells(origin).bottom())
         pipette_r.dispense(vol,plate_samples.wells(sample).bottom(downto))
         if measure_time and not robot.is_simulating:
            end_time = monotonic()
            log.warning(f'Dispensed from {module.get_name()}:{origin} to {sample} at T={end_time-start_time}')
         pipette_r.blow_out(plate_samples.wells(sample).bottom(downto))

   if new_tip == 'once':
      pipette_r.drop_tip()

   pipette_r.set_flow_rate(aspirate=flow_rate['a_r'], dispense=flow_rate['d_r'])

def samples_trash(vol, new_tip='once', safe_flow_rate=15, downto=0):

   # safe_flow_rate sets the aspirate rate

   pipette_r.set_flow_rate(aspirate = safe_flow_rate, dispense = 50)
   times = vol // pipette_r.max_volume
   vol = vol % pipette_r.max_volume

   if new_tip == 'once':
      custom_pick_up_tip()


   for sample in [f'A{i}' for i in range(1, 10)]:

      if new_tip == 'always':
         custom_pick_up_tip()

      for x in range(1,times+1):

         pipette_r.aspirate(pipette_r.max_volume,plate_samples.wells(sample).bottom(downto))
         pipette_r.dispense(pipette_r.max_volume,trash_liquid)
         pipette_r.blow_out(trash_liquid)

      if vol > 0:
         pipette_r.aspirate(vol,plate_samples.wells(sample).bottom(downto))
         pipette_r.dispense(vol,trash_liquid)
         pipette_r.blow_out(trash_liquid)

      if new_tip == 'always':
         pipette_r.drop_tip()

   if new_tip == 'once':
      pipette_r.drop_tip()

   pipette_r.set_flow_rate(aspirate=flow_rate['a_r'], dispense=flow_rate['d_r'])


def robot_wait(func=None, timer=None):

    # You can specify a function to run <timer> minutes after the robot starts waiting
    if func is not None:
       if robot.is_simulating():
          func()
       start_time = perf_counter()
       duration = 60*timer
       started = False
    
    if not robot.is_simulating():
       robot.comment("Waiting...")
       robot._driver.turn_on_red_button_light()
       while not robot._driver.read_button():
          if func is not None and not started:
             now = perf_counter()
             if now-start_time > duration:
                started = True
                func()
          sleep(0.5)

       robot._driver.turn_on_blue_button_light()
   
def tween_wash(times=3):

   start_time = perf_counter()
   
   # (3) Lavado x3 con PBS 1x tween 0.1
   for x in range(1,times+1):
      storage_samples(['A1'],200, new_tip='once', downto = 11.7)
      
      robot_wait()
      
      if x < 3:
         samples_trash(200, new_tip='always', downto = 0)

   end_time = perf_counter()
   log.warning(f'Tween wash duration: {end_time-start_time}')


def dilutions():

   pipette_l.transfer(1440, Eppendorf.wells('C1'), Eppendorf.wells('B1'))
   pipette_l.transfer(160, td_lab.wells('A4'), Eppendorf.wells('B1'), mix_before=(3,150), blow_out=True)
   pipette_l.transfer(1440, Eppendorf.wells('C2'), Eppendorf.wells('B2'))
   pipette_l.transfer(160, td_lab.wells('B4'), Eppendorf.wells('B2'), mix_before=(3,150), blow_out=True)
   pipette_l.transfer(630, Eppendorf.wells('C3'), Eppendorf.wells('B3'))
   pipette_l.transfer(70, td_lab.wells('C4'), Eppendorf.wells('B3'), mix_before=(3,80), blow_out=True)

   



# ============== START ===========================================================================
       
robot._driver.turn_on_rail_lights()
pipette_l.set_flow_rate(aspirate=flow_rate['a_l'], dispense=flow_rate['d_l'])

# (-2)
# TODO ESTE PASO TIENE QUE ASPIRAR CASI AL FONDO. CALIBRAR A 10.7 mm bajo el tope del pozo
samples_trash(200, new_tip='always', downto = 0)
tween_wash()

# (1) 200ul of PBS 1x BSA 5% to plate
# TODO BAJAR MAS
storage_samples(['A1','A2','A3','A4','A5','A6','A7','A8','A9'],200, module = plate_buffers, safe_flow_rate=15, mix=True, downto=10)

# (2) Incubar 1h y estructurizar aptamers y retirar PBS - PAUSE (Hand made)
robot_wait()

# (3) Lavado con tween
tween_wash()

# (5) Add 100ul from each apt to the plates

for epp,dest in [('A1','A1'), ('A2','A2'), ('A3','A3'), ('A4','A7'), ('A4','A8'), ('A5','A4'), ('A6','A5'), ('A7','A6'), ('A7','A9')]:
   # source, dest

   pipette_l.pick_up_tip()

   for pos in range(1,6):
      pipette_l.set_flow_rate(dispense=20)
      pipette_l.transfer(100,Eppendorf.wells(epp),plate_samples.wells(addrow(dest,pos-1)).bottom(10), new_tip='never', blow_out=True)
      pipette_l.set_flow_rate(dispense=200)

   pipette_l.drop_tip()

# Pausar para incubar 1h - PAUSE (Hand made)
robot_wait()

# (6) Lavado x3 con tween
tween_wash()

# (6.5) Diluciones anticuerpos
dilutions()

# (7) Eppendorf con anticuerpo A todos (en módulo térmico!)

for epp,dest in [('B1','A1'), ('B1','A2'), ('B1','A3'), ('B2','A4'), ('B2','A5'), ('B2','A6'), ('B3','A8'), ('B4','A7'), ('B4','A9')]:

   pipette_l.pick_up_tip()

   for pos in range(1,6):
      if '4' not in epp:
         # Don't mix aptamer buffer
         pipette_l.mix(3,50,Eppendorf.wells(epp))
      pipette_l.set_flow_rate(dispense=20)
      pipette_l.transfer(100,Eppendorf.wells(epp),plate_samples.wells(addrow(dest,pos-1)).bottom(10), new_tip='never', blow_out=True)
      pipette_l.set_flow_rate(dispense=200)

   pipette_l.drop_tip()

# Pausar para incubar 1h - PAUSE (Hand made)
robot_wait()

# (8) Lavado x3 con PBS 1x tween 0.1
tween_wash()

# (9) Add 100ul of ABTS
storage_samples(['A1','A2','A3','A4','A5','A6','A7','A8','A9'],100, module = plate_buffers, safe_flow_rate=30, measure_time=True, downto=10)

robot.turn_off_rail_lights()
robot._driver.home()
