'''
 Amplify the DNA via PCR thermocycler

'''

from opentrons import labware, instruments, modules, robot
from ninjapcr import NinjaPCR, SAMPLE_PROGRAM
from subprocess import Popen
from time import sleep
import os, sys

FINAL_HOLD = {'name': 'Final hold',
              'lid_temp': 20,
              'steps': [
                        {'type': 'step',
                         'time': 54000,
                         'temp': 20,
                         'name': 'Final Hold',
                         'ramp': 0}]}
'''
def next_loc(loc):
        if int(loc[1:]) < 12:
                n_loc = loc[0] + str(int(loc[1:])+1)
        else:
                n_loc = loc
                n_loc[0] -= 1
        return n_loc
'''

max_speed_per_axis = {
    'x': 600, 'y': 500, 'z': 150, 'a': 150, 'b': 40, 'c': 40}
robot.head_speed(**max_speed_per_axis)


def pcr(plate, pipette, tiprack, thermocycler, primer_well, mm_well, dna_well, water_well, first_mix, second_mix, third_mix):
        # Attempt to connect to the thermocycler

        if not thermocycler.connected:
                thermocycler.connect()

        robot._driver.turn_on_rail_lights()
        
        #location = 'H1'
        #pipette_r.pick_up_tip(location = tiprack.wells(location))
        volumes = [[25,25,25],[22, 27],[6,6],[20]]
        dispense_m = {primer_well:[first_mix,second_mix],mm_well:[first_mix,second_mix,third_mix],dna_well:[second_mix],water_well:[first_mix,third_mix]}

        # (1) MasterMix
        for sample,volume_l in zip([mm_well,water_well, primer_well, dna_well], volumes):
                
                #pipette.pick_up_tip(location = tiprack.wells(location))
                #location = next_loc(location)
                pipette.pick_up_tip()
                
                for wells,volume in zip(dispense_m[sample],volume_l):
                        
                        pipette.aspirate(volume,plate.wells(sample).bottom(1), rate=0.5)
                        pipette.dispense(plate.wells(wells))
                        pipette.blow_out(plate.wells(wells).top(-5))
                        pipette.touch_tip()
                        pipette.move_to(plate.wells(wells).top(10))
                        pipette.delay(seconds=5)

                pipette.drop_tip()
                        
                #pipette.pick_up_tip(location = tiprack.wells(location))
                        
        pipette.transfer(50, plate.wells('A1'), thermocycler.labware.wells('A1'), blow_out=True)
        #location = next_loc(location)
        #pipette.pick_up_tip(location = tiprack.wells(location))
        pipette.transfer(50, plate.wells('B1'), thermocycler.labware.wells('A2'), blow_out=True)
        #location = next_loc(location)
        #pipette.pick_up_tip(location = tiprack.wells(location))
        pipette.transfer(50, plate.wells('C1'), thermocycler.labware.wells('A3'), blow_out=True)

        PROGRAM = {'name': 'Heat',
                   'lid_temp': 110,
                   'steps': [{
                           'type': 'step',
                           'time': 30,
                           'temp': 65,
                           'name': 'Heat',
                           'ramp': 0}]}

        robot._driver.turn_off_rail_lights()
        
        thermocycler.wait_for_program(PROGRAM)
        robot.home()
'''
def execute_move(function, args):

        if robot.is_simulating():
                function(*args)

        else:
                # When the robot starts moving light goes on and
                # button turns red
                robot._driver.turn_on_rail_lights()
                robot._driver.turn_on_red_button_light()
                cmd  = "ffplay -nodisp -autoexit /mnt/usbdrive/robot.mp3 &> /dev/null"
                cmd2 = "pkill ffplay"
                cmd_video = 'ffmpeg -video_size 320x240 -i /dev/video0 -t 00:06:00 -metadata:s:v rotate="180" video.mp4'

                # Will play while door is opened
                while not robot._driver.read_window_switches():

                        p = Popen(cmd,shell=True)

                        while not robot._driver.read_window_switches() and p.poll() is None:
                                sleep(.1)
                        if robot._driver.read_window_switches() and p.poll() is None:
                                os.system(cmd2)
                try:
                        p = Popen(cmd_video, shell=True)
                        function(*args)
                except:
                        print("Error calling function " + function().__name__ + "\n")

                robot._driver.turn_off_rail_lights()
                robot._driver.turn_on_blue_button_light()
'''
# Run PCR as an independent protocol

# Labware and module initialization

if "eppendorf_rack" not in labware.list():
    labware.create(
        "eppendorf_rack",
        grid=(12,8),
        spacing=(9,9),
        diameter=5,
        depth=21,
        volume=50)

plate = labware.load('eppendorf_rack', slot='8')
tiprack = labware.load('opentrons-tiprack-300ul', slot='6')
ninja = NinjaPCR(slot='10', simulating = robot.is_simulating())

primer_well = 'A2'
mm_well = 'B2'
dna_well = 'C2'
water_well = 'D2'

first_mix = 'A1'
second_mix = 'B1'
third_mix = 'C1'

pipette_l = instruments.P50_Single(mount='left', tip_racks=[tiprack])

args = [plate, pipette_l, tiprack, ninja, primer_well, mm_well, dna_well, water_well, first_mix, second_mix, third_mix]

pcr(*args)


