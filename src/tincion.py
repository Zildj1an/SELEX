'''
Dyeing of the cells

'''
from opentrons import labware, instruments, modules, robot
from opentrons.data_storage import database
from opentrons.drivers.rpi_drivers import gpio

metadata = {
   'protocolName' : 'Dyeing',
   'description'  : 'Dyeing of the cells',
   'source'       : 'https://github.com/Zildj1an/SELEX'
}

# X,Y,Z,A speeds for lateral,front and vertical motion for left and right
# B,C plunger speed for motor
max_speed_per_axis = {'x': 600,'y': 400,'z': 125,'a': 125,'b': 40,'c': 40}
robot.head_speed(**max_speed_per_axis)

database.delete_container('Storage_Module')

storage_name = 'Storage_Module'
if storage_name not in labware.list():
   Storage = labware.create(
      storage_name,
      grid = (8,4),
      spacing = (15,20),
      diameter = 10,
      depth  = 100,
      volume = 100)

Storage          = labware.load(storage_name,    slot = '8')
tiprack          = labware.load('tiprack-10ul',  slot = '6')
#tiprack2         = labware.load('tiprack-10ul',  slot = '3')
plate_samples    = labware.load('96-flat',       slot = '2') 
trash            = labware.load('trash-box',     slot = '12', share = True)

pipette_r = instruments.P50_Multi(mount = 'right', tip_racks=[tiprack], trash_container = trash)
pipette_r.set_flow_rate(aspirate = 50, dispense = 100)

def samples_trash():

   pipette_r.pick_up_tip()

   # TODO cuanto (200 salvo último paso, 220)

   for sample in [('A' + '{}').format(i) for i in range(1, 13)]:
        pipette_r.aspirate(50,plate_samples.wells(sample))
        pipette_r.dispense(50,trash)

   pipette_r.drop_tip()

def storage_samples(where):
     
    pipette_r.pick_up_tip()

    # TODO cuanto

    for sample in [('A' + '{}').format(i) for i in range(1, 13)]:
        pipette_r.aspirate(50,Storage.wells(where))
        pipette_r.dispense(50,plate_samples.wells(sample))

    pipette_r.drop_tip()

# Hasta la columna 6 completo, y la mitad del arriba del resto
# La pipeta no toca el pocillo. En las ultimas seis columnas coger solo la mitad
# Aspira 50 de la columna a la basura, 4 veces por columna

robot._driver.turn_on_rail_lights()

samples_trash()

# Por columna, 50 de PBS (en el storage 1 columna) hasta llegar a 200 en todas
# De 50 en 50 por columna (ojo con lo de las pipetas)

storage_samples('A1')
samples_trash()

# 200 ul de cristal violeta (2a columna), IGUAL que antes pero con la segunda columna del storage

storage_samples('A2')

# Con un boton
if not robot.is_simulating():
    while not gpio.read(gpio.INPUT_PINS['BUTTON_INPUT']):
         print("Waiting...")

# EN LA SIGUIENTE PARTE: Tincion 2
# Tinte 200ul a la basura

for x in range(1,4):

    samples_trash()

    # En la 5a columna hay agua
    # 220 ul de agua a cada uno de los pocillos

    storage_samples('A5')

    # Cambiada la punta
    # Los 220 ul de agua del pocillo a la basura

robot._driver.turn_off_rail_lights()
robot._driver.home()

