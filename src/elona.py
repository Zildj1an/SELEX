'''
 Elona Protocol

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

storage_name = 'Storage_Module'
if storage_name not in labware.list():
   Storage = labware.create(
      storage_name,
      grid = (10,1),
      spacing = (12.5,0),
      diameter = 9,
      depth  = 40,
      volume = 200000)


Storage          = labware.load(storage_name, slot = 5)
plate_samples    = labware.load('96-flat',       slot = 2)
plate_buffers    = labware.load('96-flat',       slot = 3)
trash_liquid     = labware.load('corning_384_wellplate_112ul_flat', slot = 4)
Eppendorf        = labware.load('Eppendorf_Samples', slot = 10)
tiprack_l        = labware.load('opentrons-tiprack-300ul', slot=9)
tiprack_r        = labware.load('opentrons-tiprack-10ul', slot=6)

# [2] Pipettes

pipette_l = instruments.P300_Single(mount = 'left', tip_racks=[tiprack_l])
pipette_r = instruments.P50_Multi(mount = 'right')

flow_rate = {'a_l': 300, 'd_l': 10, 'a_r': 50, 'd_r': 50}

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
   

def storage_samples(where, vol, new_tip='once', module = Storage, safe_flow_rate=10):

   pipette_r.set_flow_rate(aspirate = 50, dispense = safe_flow_rate)

   if new_tip == 'once':
      pick_up_multi()
   
   times = vol // pipette_r.max_volume

   vol = vol % pipette_r.max_volume

   if len(where) < 3:
      # Support for different origins
      where *= 3
   
   for sample,origin in zip([f'A{i}' for i in range(1, 4)], where):

      # For every well in A1 - A3

      for x in range(1,times+1):
      
         pipette_r.aspirate(pipette_r.max_volume,module.wells(origin))
         pipette_r.dispense(pipette_r.max_volume,plate_samples.wells(sample).bottom(3))
         pipette_r.blow_out(plate_samples.wells(sample))

      if vol > 0:
         pipette_r.aspirate(vol,module.wells(origin))
         pipette_r.dispense(vol,plate_samples.wells(sample).bottom(3))
         pipette_r.blow_out(plate_samples.wells(sample))

   if new_tip == 'once':
      pipette_r.drop_tip()

   pipette_r.set_flow_rate(aspirate=flow_rate['a_r'], dispense=flow_rate['d_r'])
         

def samples_trash(vol, discard=False, safe_flow_rate=10):

   pipette_r.set_flow_rate(aspirate = safe_flow_rate, dispense = 50)
   times = vol // pipette_r.max_volume
   vol = vol % pipette_r.max_volume
   
   for sample in [f'A{i}' for i in range(1, 4)]:

      if discard:
         pick_up_multi()
      
      for x in range(1,times+1):
         
         pipette_r.aspirate(pipette_r.max_volume,plate_samples.wells(sample).bottom(-0.5))
         pipette_r.dispense(pipette_r.max_volume,trash_liquid.wells(sample))
         pipette_r.blow_out(trash_liquid.wells(sample))
         pipette_r.touch_tip()

      if vol > 0:
         pipette_r.aspirate(vol,plate_samples.wells(sample).bottom(-0.5))
         pipette_r.dispense(vol,trash_liquid.wells(sample))
         pipette_r.blow_out(trash_liquid.wells(sample))
         pipette_r.touch_tip()
         
      if discard:
         pipette_r.drop_tip()
            
   pipette_r.set_flow_rate(aspirate=flow_rate['a_r'], dispense=flow_rate['d_r'])
   
      
robot._driver.turn_on_rail_lights()


pipette_l.set_flow_rate(aspirate=flow_rate['a_l'], dispense=flow_rate['d_l'])


# (1) 200ul of PBS 1x BSA 5% to plate
storage_samples(['A1','A2','A3'],200, module = plate_buffers, safe_flow_rate=5)

# (2) Estructurizar aptamers y retirar PBS - PAUSE (Hand made)
if not robot.is_simulating():
   robot.comment("Waiting...")
   while not robot._driver.read_button():
      sleep(0.5)


pick_up_multi()
# (3) Lavado x3 con PBS 1x tween 0.1
for x in range(1,4):
    storage_samples(['A5'],200, new_tip='never')
    samples_trash(200)

pipette_r.drop_tip()

# (4) Retirar a mano - PAUSE (Hand made)
if not robot.is_simulating():
   robot.comment("Waiting...")
   while not robot._driver.read_button():
      sleep(0.5)

# (5) Add 100ul from each apt to the plates

for epp, control_neg in [('A',1),('B',2),('C',3)]:

     pipette_l.pick_up_tip()
     eppend = epp + '1'

     for pos in range(1,4):
         pipette_l.transfer(100,Eppendorf.wells(eppend),plate_samples.wells(epp + str(pos)), new_tip='never', mix_before=(3,50), blow_out=True)

     pipette_l.transfer(100,Eppendorf.wells(eppend),plate_samples.wells('D' + str(control_neg)), new_tip='never', mix_before=(3,50), blow_out=True)
     pipette_l.drop_tip()

# (6) Lavado x3 con Buffer

pick_up_multi()

for x in range(1,4):
    storage_samples(['A3'],200, new_tip='never')
    samples_trash(200)

pipette_r.drop_tip()

# Pausar para fregadero - PAUSE (Hand made)
if not robot.is_simulating():
   robot.comment("Waiting...")
   while not robot._driver.read_button():
      sleep(0.5)

# (7) Eppendorf con anticuerpo A todos (en módulo con hielo!!)
for well in [f'{j}{i}' for i in range(1, 4) for j in ['A','B','C','D']]:
   pipette_l.transfer(100,Eppendorf.wells('D1'),plate_samples.wells(well), new_tip='once', mix_before=(3,50), blow_out=True)

# Pausar para fregadero - PAUSE (Hand made)
if not robot.is_simulating():
   robot.comment("Waiting...")
   while not robot._driver.read_button():
      sleep(0.5)


pick_up_multi()
# (8) Lavado x3 con PBS 1x tween 0.1
for x in range(1,4):
    storage_samples(['A5'],200, new_tip='never')
    samples_trash(200)

pipette_r.drop_tip()

# Pausar para fregadero - PAUSE (Hand made)
if not robot.is_simulating():
   robot.comment("Waiting...")
   while not robot._driver.read_button():
      sleep(0.5)
      
# (9) Add 100ul of ABTS
storage_samples(['A4','A5','A6'],100, module = plate_buffers)

robot._driver.home()
