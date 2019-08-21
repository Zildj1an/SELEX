'''
Dyeing of the cells
VIEW TIPRACK SCHEMA

'''
from opentrons import labware, instruments, modules, robot
from opentrons.data_storage import database
from time import sleep

metadata = {
   'protocolName' : 'Dyeing',
   'description'  : 'Dyeing of the cells',
   'source'       : 'https://github.com/Zildj1an/SELEX'
}

# X,Y,Z,A speeds for lateral,front and vertical motion for left and right
# B,C plunger speed for motor
#max_speed_per_axis = {'x': 600,'y': 400,'z': 125,'a': 125,'b': 40,'c': 40}
max_speed_per_axis = {'x': 400,'y': 200,'z': 80,'a': 80,'b': 20,'c': 20}
robot.head_speed(**max_speed_per_axis)

storage_name = 'Storage_Module'
if storage_name not in labware.list():
   Storage = labware.create(
      storage_name,
      grid = (10,5),
      spacing = (12,0),
      diameter = 10,
      depth  = 50,
      volume = 41)

Storage          = labware.load('usascientific_12_reservoir_22ml', slot = '8')
tiprack          = labware.load('opentrons-tiprack-300ul',  slot = '6')
tiprack2         = labware.load('opentrons-tiprack-300ul',  slot = '3')
plate_samples    = labware.load('96-flat',       slot = '2')
trash_liquid     = labware.load('corning_384_wellplate_112ul_flat', slot = '4')
trash            = labware.load('trash-box',    slot = '12', share = True)        # Trash

pipette_r = instruments.P50_Multi(mount = 'right', tip_racks=[tiprack,tiprack2], trash_container = trash)

def samples_trash(vol, discard=False):

   pipette_r.set_flow_rate(aspirate = 5, dispense = 50)

   if not discard:
      pipette_r.pick_up_tip()

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

   if not discard:
      pipette_r.drop_tip()


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

   pipette_r.drop_tip()

# Hasta la columna 6 completo, y la mitad del arriba del resto
# La pipeta no toca el pocillo. En las ultimas seis columnas coger solo la mitad
# Aspira 50 de la columna a la basura, 4 veces por columna

robot._driver.turn_on_rail_lights()

samples_trash(200)

# Por columna, 50 de PBS (en el storage 1 columna) hasta llegar a 200 en todas
# De 50 en 50 por columna (ojo con lo de las pipetas)

storage_samples('A1', 200)
samples_trash(200)

# Repetimos lavado
storage_samples('A1', 200)
samples_trash(200)

# 150 ul de cristal violeta (2a columna), IGUAL que antes pero con la segunda columna del storage

storage_samples('A2', 150)

# Pause 20 mins

# Or pause
if not robot.is_simulating():
   robot.comment("Waiting...")
   while not robot._driver.read_button():
      sleep(0.5)


samples_trash(150)

# EN LA SIGUIENTE PARTE: Tincion 2
# Tinte 200ul a la basura

for i in range(3,6):

    # En la 5a columna hay agua
    # 220 ul de agua a cada uno de los pocillos
    storage_samples(f'A{i}', 220)
    # AGITAR TODO
    samples_trash(220)

robot._driver.turn_off_rail_lights()
robot._driver.home()

