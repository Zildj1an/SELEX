'''
 Amplify the DNA via PCR

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

def next_loc(loc):
        if int(loc[1:]) < 12:
                n_loc = loc[0] + str(int(loc[1:])+1)
        else:
                n_loc = loc
                n_loc[0] -= 1
        return n_loc

def pcr(plate, pipette_r, tiprack, thermocycler, primer_well, mm_well, dna_well, water_well, first_mix, second_mix, third_mix):
        # Attempt to connect to the thermocycler

        if not thermocycler.connected:
                thermocycler.connect() 


        location = 'H5'
                
        pipette_r.pick_up_tip(location = tiprack.wells(location))

        volumes = [5,25,20, [20, 10]]

        '''
        # (1) MasterMix
        pipette_r.distribute(volumes[1], plate.wells(mm_well), [plate.wells(first_mix), plate.wells(second_mix), plate.wells(third_mix)], new_tip='never')

        pipette_r.drop_tip()
        location = next_loc(location)
        pipette_r.pick_up_tip(location = tiprack.wells(location))
        '''
        '''x
        # (2) Water
        pipette_r.distribute(volumes[3], plate.wells(water_well), [plate.wells(first_mix), plate.wells(third_mix)], new_tip='never')

        pipette_r.drop_tip()
        location = next_loc(location)
        pipette_r.pick_up_tip(location = tiprack.wells(location))


        # (3) Priemrs
        pipette_r.distribute(volumes[0], plate.wells(primer_well), [plate.wells(first_mix), plate.wells(second_mix)], new_tip='never')

        pipette_r.drop_tip()
        location = next_loc(location)
        pipette_r.pick_up_tip(location = tiprack.wells(location))

        # (4) DNA
        pipette_r.distribute(volumes[2], plate.wells(dna_well), [plate.wells(second_mix)], new_tip='never')
        
        pipette_r.drop_tip()
        location = next_loc(location)
        '''
        #pipette_r.pick_up_tip(location = tiprack.wells(location))

        pipette_r.transfer(50, plate.wells('A1'), thermocycler.labware.wells('A1'))

        location = next_loc(location)
        pipette_r.pick_up_tip(location = tiprack.wells(location))

        pipette_r.transfer(50, plate.wells('B1'), thermocycler.labware.wells('A2'))

        location = next_loc(location)
        pipette_r.pick_up_tip(location = tiprack.wells(location))

        pipette_r.transfer(50, plate.wells('C1'), thermocycler.labware.wells('A3'))


        program = {'name': 'Heat',
                   'lid_temp': 110,
                   'steps': [{
                           'type': 'step',
                           'time': 30,
                           'temp': 65,
                           'name': 'Heat',
                           'ramp': 0}]}
        
        thermocycler.wait_for_program(SAMPLE_PROGRAM)
        
        robot.home()

        thermocycler.wait_for_program(FINAL_HOLD)
                   


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
                        

        
# Run PCR as an independent protocol

# Labware and module initialization

plate = labware.load('96-flat', slot='8')
tiprack = labware.load('opentrons-tiprack-300ul', slot='6')
ninja = NinjaPCR(slot='10', simulating = robot.is_simulating())

primer_well = 'A2'
mm_well = 'B2'
dna_well = 'C2'
water_well = 'D2'

first_mix = 'A1'
second_mix = 'B1'
third_mix = 'C1'


pipette_r = instruments.P50_Multi(mount='right')

execute_move(pcr, [plate, pipette_r, tiprack, ninja, primer_well, mm_well, dna_well, water_well, first_mix, second_mix, third_mix])
