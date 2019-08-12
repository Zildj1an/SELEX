"""
@author Carlos Bilbao, Pablo Villalobos
@date July 12th, 2019
@version 1
 __    __  __    ____  __
/ _\  /__\/ /   /__\ \/ /
\ \  /_\ / /   /_\  \  /
_\ \//__/ /___//__  /  \
\__/\__/\____/\__/ /_/\_\

"""

from opentrons import labware, instruments, modules, robot
from opentrons.data_storage import database
from ninjapcr import NinjaPCR
from subprocess import Popen
from time import sleep
import os, requests, logging, sys

metadata = {
	'protocolName' : 'Selex',
	'author'       : 'Carlos Bilbao, Pablo Villalobos',
	'description'  : 'Selex protocol for evolving aptamers',
	'source'       : 'https://github.com/Zildj1an/SELEX'
}

# [0] Ninja-PCR API

URL_PCR = "http://ninjapcr.local/command"
URL_AUX = "http://thermaux.local/command"

# [1] Labware

# X,Y,Z,A speeds for lateral,front and vertical motion for left and right
# B,C plunger speed for motor

max_speed_per_axis = {'X': 600,'Y': 400,'Z': 125,'A': 125,'B': 40,'C': 40}
robot.head_speed(**max_speed_per_axis)

database.delete_container('Thermic_Module')

thermic_name = 'Thermic_Module' #TODO check
if thermic_name not in labware.list():
    thermic = labware.create(
        thermic_name,                         # Labware Name
        grid     = (4, 4),                    # Amount of (columns, rows)
        spacing  = (9, 9),                    # Distances (mm) between each (column, row)
        diameter = 2,                         # Diameter (mm) of each well on the plate
        depth    = 10,                        # Depth (mm) of each well on the plate
        volume   = 50)

plate_samples    =   labware.load('96-flat',      slot ='11')                       # Samples TODO Eppendorf 1.5
tiprack          =   labware.load('tiprack-10ul', slot ='6')                        # Tipracks
magnetic         =   modules.load('magdeck',      slot ='4')                        # Magnetic Deck
plate_magnet     =   labware.load('96-flat',      slot ='4', share = True)          # Magnetic Deck plate
thermocycler     =   NinjaPCR(slot='10', simulating = robot.is_simulating())        # Ninja-PCR
thermic_module   =   labware.load(thermic_name,   slot ='1')                        # Auxiliar thermic module
trash            =   labware.load('trash-box',    slot = '12', share = True)        # Trash

# [2] Pipettes

pipette_l   = instruments.P300_Single(mount = 'left', tip_racks=[tiprack], trash_container = trash)
pipette_r   = instruments.P50_Multi(mount = 'right', tip_racks=[tiprack], trash_container = trash)
pipette_l.set_flow_rate(aspirate = 50, dispense = 100)
pipette_r.set_flow_rate(aspirate = 50, dispense = 100)

# [3] Commands

def execute_move(function, args):

        # For the simulation
        if robot.is_simulating():
                function(*args)
                return

        # When the robot starts moving light goes on and
        # button turns red
        robot._driver.turn_on_rail_lights()
        robot._driver.turn_on_red_button_light()
        cmd  = "ffplay -nodisp -autoexit /mnt/usbdrive/robot.mp3 &> /dev/null"
        cmd2 = "pkill ffplay"

        # Will play while door is opened
        while not robot._driver.read_window_switches():

               p = Popen(cmd,shell=True)

               while not robot._driver.read_window_switches() and p.poll() is None:
                      sleep(.1)
               if robot._driver.read_window_switches() and p.poll() is None:
                      os.system(cmd2)
        try:
           function(*args)
        except:
           debug_msg("Error calling function " + function().__name__ + "\n")

        robot._driver.turn_off_rail_lights()
        robot._driver.turn_on_blue_button_light()

def debug_msg(msg):

        p = Popen("echo " + msg + " >> /root/debug_file" ,shell=True)
        print(msg)

def next_loc(loc):
        if int(loc[1:]) < 12:
                n_loc = loc[0] + str(int(loc[1:])+1)
        else:
                n_loc = loc
                n_loc[0] -= 1
        return n_loc

def samples_to_pcr(args):

        pipette_l.pick_up_tip()

        for l in ['A','B','C','D']:

               pipette_l.aspirate(250,plate_samples.wells('A1'))

               for x in [(l + '{}').format(i) for i in range(1, 5)]:
                     pipette_l.dispense(50,thermocycler.labware.wells(x))

        pipette_l.drop_tip()

def samples_to([orig,dest]):

        pipette_l.pick_up_tip()

        for l in ['A','B','C','D']:

               for x in [(l + '{}').format(i) for i in range(1, 5)]:
                     pipette_l.aspirate(50,orig.labware.wells(x))

               for x in [(l + '{}').format(i) for i in range(1, 5)]:
                     pipette_l.dispense(50,dest.labware.wells(x))

        pipette_l.drop_tip()

def wash_madgeck(args):

      pipette_l.pick_up_tip()

      # TODO "Lavados"
      # Pasos:
      # 1 Liquido buffer a las pipetas del magdeck
      # pipette_r.aspirate(50,)
      # pipette_r.dispense(50,)
      # 2 magdeck.engage()
      # 3 Esperar tiempo por determinar
      sleep(1)
      # 4 Extraer liquido y repetir el paso 1
      # 5 El proceso se repite un num por determinar
      pipette_l.drop_tip()

def DNA_amplification(plate, pipette_r, tiprack, thermocycler, primer_well, mm_well, dna_well, water_well, first_mix, second_mix, third_mix):

        try:
        if not thermocycler.connected:
              thermocycler.connect()
        except:
              debug_msg("Initial Connection failed!\n")

        # Water and primer volumes have been increased by 1-2ul to account for OT pipette error
        volumes = {mm_well:[25,25,25],water_well:[22,27],primer_well:[6,6],dna_well:[20]}
        dispense_m = {primer_well:[first_mix,second_mix],mm_well:[first_mix,second_mix,third_mix],dna_well:[second_mix],water_well:[first_mix,third_mix]}

        # (1) MasterMix
        for sample in [mm_well,water_well, primer_well, dna_well]:

                #pipette.pick_up_tip(location = tiprack.wells(location))
                #location = next_loc(location)
                pipette.pick_up_tip()

                for wells,vol in zip(dispense_m[sample], volumes[sample]):

                        pipette.aspirate(vol,plate.wells(sample).bottom(1))
                        pipette.dispense(vol,plate.wells(wells))
                        pipette.blow_out(plate.wells(wells).top(-10))
                        pipette.touch_tip()

                pipette.drop_tip()

                #pipette.pick_up_tip(location = tiprack.wells(location))

        pipette.transfer(50, plate.wells('A1'), thermocycler.labware.wells('A1'))
        #location = next_loc(location)
        #pipette.pick_up_tip(location = tiprack.wells(location))
        pipette.transfer(50, plate.wells('B1'), thermocycler.labware.wells('A2'))
        #location = next_loc(location)
        #pipette.pick_up_tip(location = tiprack.wells(location))
        pipette.transfer(50, plate.wells('C1'), thermocycler.labware.wells('A3'))

        PROGRAM = {'name': 'Heat',
                   'lid_temp': 110,
                   'steps': [{
                           'type': 'step',
                           'time': 30,
                           'temp': 65,
                           'name': 'Heat',
                           'ramp': 0}]}

        thermocycler.wait_for_program(PROGRAM)

# [4] SELEX execution

logging.getLogger("opentrons").setLevel(logging.INFO)

try:
if not thermocycler.connected:
        thermocycler.connect()
except:
        debug_msg("Initial Connection failed!\n")

# (1) Warming at 90 degrees for 600 seconds (PCR)

debug_msg("Applying heat to samples...\n")
heat_program = {'name': 'Heat',
                'lid_temp': 110,
                'steps': [{
                    'type': 'step',
                    'time': 1500,
                    'temp': 90,
                    'name': 'Initial Step',
                    'ramp': 0}]}

#TODO Abrir puerta PCR
thermocycler.send_command('start',heat_program)

cold_program = {'name': 'Cold',
                'lid_temp': 4,
                'steps': [{
                    'type': 'step',
                    'time': 2500,
                    'temp': 4,
                    'name': 'Second Step',
                    'ramp': 0}]}

#thermic_module.send_command('start',cold_program) TODO

execute_move(samples_to_pcr, [None])
# TODO cerrar la puerta
# sleep(600)

# (2) Cooling at 4 degrees for 600 seconds (aux)

debug_msg("Moving samples to cool them...\n")

# COMPROBAR QUE YA ESTA A 4 GRADOS PQ DEBE ESTARLO AL MOVER
execute_move(samples_to, [thermocycler,thermic_module])

# (4) Magnentic separation

execute_move(samples_to_magdeck, [thermic_module,magdeck])

# The first time you wish to get rid of the ones stuck to the
# non-modified e.coli
# moverlo a magdeck
# magnetic.engage()

# (5) Aptamers somewhere else
# move aptamers at magdeck to cholira

# (6) Wash the magdeck (Lavados)
#execute_move(wash_magdeck,[None])

# Rest aptamers + cholira (e-choli with "cholera")
# (7) De nuevo (4),(6)

# (8) Robot must be stopped for DNA measuring
# It will resume when bottom is pressed TODO

# (9) Amplify the DNA via PCR

primer_well = 'A2'
mm_well     = 'B2'
dna_well    = 'C2'
water_well  = 'D2'
first_mix   = 'A1'
second_mix  = 'B1'
third_mix   = 'C1'
args = [plate_samples, pipette_l, tiprack, thermocycler, primer_well, mm_well, dna_well, water_well, first_mix, second_mix, third_mix]
execute_move(DNA_amplification, *args)

# (10) De nuevo (4), (6)

robot._driver.home()

