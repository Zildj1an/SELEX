'''
Separation of the cells and aptamers

'''

from opentrons import labware, instruments, modules, robot
from ninjapcr import NinjaPCR, NinjaTempDeck
from time import sleep

metadata = {
   'protocolName' : 'Separation',
   'description'  : 'Separation of cells and aptamers via MagDeck',
   'source'       : 'https://github.com/Zildj1an/SELEX'
}

HEAT_PROGRAM = {'name': 'Heat 60',
                'lid_temp': 30,
                'steps': [{
                    'type': 'step',
                    'time': 3600,
                    'temp': 60,
                    'name': 'Final Hold',
                    'ramp': 0}]}

def separate(magdeck, thermocycler, md_lab, td_lab, tc_lab, samples, tiprack, pipette, md_well, n_well, md_offset, engage_wait_time,plunger_speeds):

    # Inner functions
    def engage():
        magdeck.engage(offset=md_offset)
        pipette.delay(seconds=engage_wait_time)

    def mix(times = 3, quantity = 150, well = md_lab.wells('A1')):
        pipette.set_flow_rate(aspirate=plunger_speeds['aspirate_mix'],
                              dispense=plunger_speeds['dispense_mix'])
        pipette.mix(times, quantity, well)
        pipette.set_flow_rate(aspirate=plunger_speeds['aspirate_normal'],
                              dispense=plunger_speeds['dispense_normal'])
    def stop_thermocycler():
        # Returns True if the lid is open, False otherwise
        thermocycler.send_command('stop')
        sleep(5)
        status = thermocycler.get_status()
        return thermocycler.simulating or (status['lid_closed'] == '0')

    thermocycler.connect()

    # (1) Mix beads in thermal module
    pipette.pick_up_tip()
    mix(3, 300, td_lab.wells('A1'))

    # (2,3) Transfer 600ul beads to magdeck
    pipette.transfer(600, td_lab.wells('A1'), md_well)

    # (4)
    engage()

    # (5) Store 600ul from magdeck
    pipette.transfer(600, md_well, td_lab.wells('A1'))

    for i in range(1,5):

        # (6,7) Aspirate buffer and mix with beads
        pipette.pick_up_tip()
        pipette.transfer(300, samples.wells('D1'), md_well, new_tip='never')

        # (8)
        magdeck.disengage()

        # (9)
        mix(3, 50, md_well)
        pipette.drop_tip()

        # (10)
        engage()

        # (11) Move 300ul from magdeck
        pipette.transfer(300, md_well, td_lab.wells('A2'))

        # (12) Repeat (total of 4 times)

    # (13,14) Trasfer buffer to magdeck
    pipette.transfer(100, samples.wells('D1'), md_well)

    # (15) HASTA AQUI ACTIVACION MAGNETIC BEADS (bolas)
    magdeck.disengage()

    # (16) Transfer PCR mix to magdeck
    pipette.pick_up_tip()
    mix(3,40, n_well)
    pipette.transfer(50, n_well, md_well, new_tip='never')

    # Prepare thermocycler: heat to 60º
    thermocycler.send_command('start', program = HEAT_PROGRAM)

    for i in range(1,6):
        mix(1, 150, md_well)
        pipette.delay(120)

    pipette.set_flow_rate(aspirate=200, dispense=200)
    pipette.move_to(md_well)

    # (19)
    engage()

    # (20) Move 150ul to A3
    pipette.transfer(150, md_well, td_lab.wells('A3'))

    for i in range(1,3):

        # (21,22) Transfer another buffer to magdeck
        pipette.pick_up_tip()
        pipette.transfer(200, samples.wells('D2'), md_well, new_tip='never')

        # (23)
        magdeck.disengage()
        mix(3,200,md_well)
        pipette.drop_tip()

        # (24)
        engage()

        # (26) Move 200ul
        pipette.transfer(200, md_well, td_lab.wells('A4'))

        # (27) Repeat

    for i in range(1,3):

        # (28,29) Transfer 50ul NOOH to magdeck
        pipette.pick_up_tip()
        pipette.transfer(50, samples.wells('D3'), md_well, new_tip='never')

        # (30,31)
        magdeck.disengage()
        for x in range(1,5):
            mix(5, 50, md_well)
            pipette.delay(60)

        pipette.drop_tip()

        # (32)
        engage()

        # (33) Store 50ul at 4ºC in well Bi
        pipette.pick_up_tip()
        pipette.transfer(50, md_well, td_lab.wells('B1'), new_tip='never')
        pipette.blow_out(td_lab.wells('B1'))

        # (34) Repeat

    # (35,36) Transfer 200ul ammonia to magdeck
    pipette.pick_up_tip()
    pipette.transfer(200, samples.wells('D4'), md_well, new_tip='never')

    # (37)
    magdeck.disengage()
    mix(5, 200, md_well)

    # Incubar a 60ºC: abrir ninja, transferir samples, cerrar ninja

    if stop_thermocycler():
        pipette.distribute(100, md_well, tc_lab.wells('A2', 'A3'))
    else:
        raise Exception("Could not open thermocycler lid. Stopping")
    pipette.drop_tip()
    thermocycler.send_command('start', program = HEAT_PROGRAM)

    # (38) Incubate for 10m
    pipette.delay(600)

    # (39) Transfer beads to MagDeck and engage
    if stop_thermocycler():
          pipette.consolidate(100, tc_lab.wells('A2', 'A3'), md_well)
    else:
          raise Exception("Could not stop PCR")

    engage()

    # (40) Move 200ul
    pipette.transfer(200, md_well, tc_lab.wells('B2'))

    for m in range(1,4):
        # (43)
        magdeck.disengage()

        pipette.transfer(100, samples.wells('D5'), md_well)

        #mix --que coño es esto y que hace aqui fdo Carlos

        engage()

        # (44) Store 300ul at 4ºC
        pipette.transfer(100, md_well, td_lab.wells('B3'))
        pipette.blow_out(td_lab.wells('B3'))

        # (45) Repeat

    # (46) Add 600 ul from A1 to magdeck
    pipette.transfer(600, td_lab.wells('A1'), md_well)
    mix(5,300,md_well)
    magdeck.disengage()

plate_eppendorf = 'Eppendorf_Samples'
if plate_eppendorf not in labware.list():
   Eppendorf = labware.create(
      plate_eppendorf,
      grid = (8,4),
      spacing = (15,20),
      diameter = 10,
      depth  = 35,
      volume = 100)


magdeck_plate = 'MagDeck_24'
if magdeck_plate not in labware.list():
    labware.create(
        magdeck_plate,
        grid = (6,4),
        spacing = (18, 18),
        diameter = 10,
        depth = 41,
        volume = 1500)

if "eppendorf_rack" not in labware.list():
    labware.create(
        "eppendorf_rack",
        grid=(12,8),
        spacing=(9,9),
        diameter=5,
        depth=30,
        volume=50)

modules.magdeck.LABWARE_ENGAGE_HEIGHT[magdeck_plate] = 10

# MagDeck and associated labware
magdeck          = modules.load('MagDeck', slot=4)
md_lab           = labware.load(magdeck_plate, slot=4, share=True)

# Thermal module. SHOULD REMAIN AT 4ºC DURING THE WHOLE PROTOCOL. TODO
tempdeck         = NinjaTempDeck(slot=1, simulating = True)
td_lab           = tempdeck.labware

# Thermocycler.
thermocycler     = NinjaPCR(slot=10, simulating = robot.is_simulating())
tc_lab           = thermocycler.labware

samples          = labware.load('Eppendorf_Samples', slot=8)
tiprack          = labware.load('opentrons-tiprack-300ul', slot=6)
tiprack2         = labware.load('opentrons-tiprack-300ul', slot=3)
liquid_trash     = labware.load('corning_384_wellplate_112ul_flat', slot = 5)
#primers       = labware.load('eppendorf_rack', slot=2)

pipette_l        = instruments.P300_Single(mount='left', tip_racks=[tiprack])#, tiprack2])

md_well          = md_lab.wells('A1')
n_well           = tc_lab.wells('A1')
md_offset        = 0
engage_wait_time = 10
plunger_speeds   = {'aspirate_mix': 300, 'dispense_mix': 300, 'aspirate_normal': 150, 'dispense_normal': 150}

args = [magdeck, thermocycler, md_lab, td_lab, tc_lab, samples, tiprack, pipette_l, md_well, n_well, md_offset, engage_wait_time, plunger_speeds]

separate(*args)

