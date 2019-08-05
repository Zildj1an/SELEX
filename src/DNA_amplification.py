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

def pcr(plate, pipette, tiprack, thermocycler, primer_well, mm_well, dna_well, water_well, first_mix, second_mix, third_mix):
        # Attempt to connect to the thermocycler

        #if not thermocycler.connected:
        #        thermocycler.connect()

        #location = 'H1'
        #pipette_r.pick_up_tip(location = tiprack.wells(location))

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

        #thermocycler.wait_for_program(PROGRAM)

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


pipette_l = instruments.P50_Single(mount='left')

args = [plate, pipette_l, tiprack, ninja, primer_well, mm_well, dna_well, water_well, first_mix, second_mix, third_mix]

pcr(*args)
