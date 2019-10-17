'''
Applies wax to paper sheets using a custom stamp

'''

from opentrons import labware, instruments, modules, robot
from time import sleep
from subprocess import Popen
import os

metadata = {
   'protocolName' : 'Dar cera, pulir cera',
   'description'  : 'Applies wax to paper sheets using a custom stamp',
   'source'       : 'https://github.com/Zildj1an/SELEX'
}

stamp_tiprack = "wax-stamp-tiprack"
if stamp_tiprack not in labware.list():
    labware.create(
        stamp_tiprack,
        grid = (4,1),
        spacing = (10,10),
        diameter = 5,
        depth = 5)

paper_sheet = "paper-sheet"
if paper_sheet not in labware.list():
    labware.create(
        paper_sheet,
        grid = (4,1),
        spacing = (12,30),
        diameter = 5,
        depth = 2)

stamps = labware.load(stamp_tiprack, slot=7)
wax = labware.load('agilent_1_reservoir_290ml', slot=4)
paper = labware.load(paper_sheet, slot=1)

pipette = instruments.P300_Single(mount='left')


robot._driver.turn_on_rail_lights()

pipette.pick_up_tip(location=stamps.wells('A1'))

for j in range(1,3):
    pipette.move_to(wax.wells('A1').top(20))
    pipette.aspirate(30)
    pipette.move_to(wax.wells('A1').top(-2))
    pipette.dispense(30)
    pipette.move_to(wax.wells('A1').top(20))
    pipette.aspirate(30)
    pipette.move_to(wax.wells('A1').top(-2))
    pipette.dispense(30)
    pipette.move_to(wax.wells('A1').top(20))
    pipette.aspirate(30)
    pipette.move_to(wax.wells('A1').top(-2))
    pipette.dispense(30)
    pipette.move_to(wax.wells('A1').top(20))

    for i in range(1,4):
        pipette.move_to(paper.wells(f'A{j}').top())
        pipette.aspirate(30)
        pipette.move_to(paper.wells(f'A{j}').top(-2))
        pipette.dispense(30)

pipette.return_tip()


robot._driver.turn_off_rail_lights()

