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

Storage          = labware.load('usascientific_12_reservoir_22ml', slot = '8')
plate_samples    = labware.load('96-flat',       slot = '2')
trash_liquid     = labware.load('corning_384_wellplate_112ul_flat', slot = '4')
Eppendorf        = labware.load(plate_eppendorf, slot = '5')
trash            = labware.load('trash-box',     slot = '12', share = True)

# [2] Pipettes

pipette_l = instruments.P50_Single(mount = 'left', tip_racks=[tiprack], trash_container = trash)
pipette_r = instruments.P50_Multi(mount = 'right', tip_racks=[tiprack], trash_container = trash)

def storage_samples(where, vol):

   pipette_r.set_flow_rate(aspirate = 50, dispense = 5)

   pipette_r.pick_up_tip()

   times = vol // pipette_r.max_volume

   for x in range(1,times+1):

      for sample in [f'A{i}' for i in range(1, 4)]:

         pipette_r.aspirate(pipette_r.max_volume,Storage.wells(where))
         pipette_r.dispense(pipette_r.max_volume,plate_samples.wells(sample).bottom(3))
         pipette_r.blow_out(plate_samples.wells(sample))

   vol = vol % pipette_r.max_volume

   if vol > 0:

      for sample in [f'A{i}' for i in range(1, 4)]:
         pipette_r.aspirate(vol,Storage.wells(where))
         pipette_r.dispense(vol,plate_samples.wells(sample).bottom(3))
         pipette_r.blow_out(plate_samples.wells(sample))

def samples_trash(vol, discard=False):

   pipette_r.set_flow_rate(aspirate = 5, dispense = 50)
   times = vol // pipette_r.max_volume

   for x in range(1,times+1):

      for sample in [f'A{i}' for i in range(1, 7)]:

           if discard:
              pipette_r.pick_up_tip()
           pipette_r.aspirate(pipette_r.max_volume,plate_samples.wells(sample).bottom(-0.5))
           pipette_r.dispense(pipette_r.max_volume,trash_liquid.wells(sample))
           pipette_r.blow_out(trash_liquid.wells(sample))
           pipette_r.touch_tip()
           if discard:
              pipette_r.drop_tip()

   vol = vol % pipette_r.max_volume

   if vol > 0:

      for sample in [f'A{i}' for i in range(1, 7)]:

         if discard:
            pipette_r.pick_up_tip()
         pipette_r.aspirate(vol,plate_samples.wells(sample).bottom(-0.5))
         pipette_r.dispense(vol,trash_liquid.wells(sample))
         pipette_r.blow_out(trash_liquid.wells(sample))
         pipette_r.touch_tip()
         if discard:
            pipette_r.drop_tip()

robot._driver.turn_on_rail_lights()

# (1) 200ul of PBS 1x BSA 5% to plate
storage_samples('A1',200)

# (2) Estructurizar aptamers y retirar PBS - PAUSE (Hand made)
sleep(30)

pipette_r.pick_up_tip()
# (3) Lavado x3 con PBS
for x in range(1,4):
    storage_samples('A1',200)
    samples_trash(200)

pipette_r.drop_tip()

# (4) Retirar a mano - PAUSE (Hand made)
sleep(30)

# (5) Add 100ul from each apt to the plates

for epp, control_neg in [('A',1),('B',2),('C',3)]:

     pipette_l.pick_up_tip()
     eppend = epp + '1'

     for pos in range(1,4):
         pipette_l.transfer(100,Eppendorf.wells(eppend),plate_samples.wells(epp + str(pos)), new_tip='never', mix_before=(3,50), blow_out=True)

     pipette_l.transfer(100,Eppendorf.wells(eppend),plate_samples.wells('D' + str(control_neg)), new_tip='never', mix_before=(3,50), blow_out=True)
     pipette_l.drop_tip()

# (6) Lavado x3 con Buffer

pipette_r.pick_up_tip()

for x in range(1,4):
    storage_samples('A3',200)
    samples_trash(200)

pipette_r.drop_tip()

# (7) Pausar para fregadero - PAUSE (Hand made)
sleep(30)

# (8) Eppendorf con anticuerpo A todos (en módulo con hielo!!)

for pos in range(1,4):
         pipette_l.transfer(100,Eppendorf.wells('D1'),plate_samples.wells('A' + str(pos)), new_tip='never', mix_before=(3,50), blow_out=True)

# (9) Add 100ul of ABTS
storage_samples('A6',100)

robot._driver.home()
