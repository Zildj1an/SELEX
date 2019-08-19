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


    
    
def separate(magdeck, thermocycler, md_lab, td_lab, tc_lab, samples, tiprack, liquid_trash, pipette, md_well, n_well, md_offset, engage_wait_time):

    pipette.pick_up_tip()
    pipette.set_flow_rate(aspirate=300, dispense=300)
    pipette.mix(3, 150, md_lab.wells('A1'))
    pipette.set_flow_rate(aspirate=200, dispense=200)
    pipette.drop_tip()

    magdeck.engage()

    pipette.delay(seconds=30)

    magdeck.disengage()

    
    
    '''
    thermocycler.connect()
    
    pipette.set_flow_rate(aspirate=200, dispense=200)

    # (1) Mix beads in thermal module
    pipette.pick_up_tip()
    pipette.set_flow_rate(aspirate=50, dispense=50)
    pipette.mix(3, 50, td_lab.wells('A1'))
    pipette.set_flow_rate(aspirate=200, dispense=200)
    
    # (2,3) Transfer 300ul beads to magdeck
    pipette.transfer(300, td_lab.wells('A1'), md_well)
    
    # (4)
    magdeck.engage(offset=md_offset)
    pipette.delay(seconds=engage_wait_time)
    
    # (5) Discard 300ul from magdeck
    pipette.transfer(300, md_well, liquid_trash.wells('A1'))
    
    for i in range(1,4):
    
        # (6,7) Aspirate buffer and mix with beads
        pipette.pick_up_tip()
        pipette.transfer(100, samples.wells('D1'), md_well, new_tip='never')
        
        # (8)
        magdeck.disengage()
        
        # (9)
        pipette.set_flow_rate(aspirate=50, dispense=50)
        pipette.mix(3, 50, md_well)
        pipette.set_flow_rate(aspirate=200, dispense=200)
        pipette.drop_tip()
        
        # (10)
        magdeck.engage(offset=md_offset)
        pipette.delay(seconds=engage_wait_time)
        
        # (11) Discard 100ul from magdeck
        pipette.transfer(100, md_well, liquid_trash.wells('A1'))
        
        # (12) Repeat

    # (13,14) Trasfer buffer to magdeck
    pipette.transfer(100, samples.wells('D1'), md_well)

    
    # (15) Transfer PCR mix to magdeck
    pipette.pick_up_tip()
    pipette.transfer(50, n_well, md_well, new_tip='never')

    # Prepare thermocycler: heat to 60º
    thermocycler.send_command('start', program = HEAT_PROGRAM)
    
    # (16)
    magdeck.disengage()
    
    # (17)
    pipette.set_flow_rate(aspirate=50, dispense=50)
    pipette.mix(5, 50, md_well)
    pipette.set_flow_rate(aspirate=200, dispense=200)
    pipette.move_to(md_well)

    # (18) Incubate and mix for 10 minutes
    pipette.delay(minutes=10)

    pipette.drop_tip()
        
    # (19)
    magdeck.engage(offset=md_offset)
    pipette.delay(seconds=engage_wait_time)


    # (20) Discard 150ul
    pipette.transfer(150, md_well, liquid_trash.wells('A1'))

    for i in range(1,3):

        # (21,22) Transfer another buffer to magdeck
        pipette.pick_up_tip()
        pipette.transfer(100, samples.wells('D2'), md_well, new_tip='never')

        # (23)
        magdeck.disengage()
        pipette.set_flow_rate(aspirate=50, dispense=50)
        pipette.mix(3,50,md_well)
        pipette.set_flow_rate(aspirate=200, dispense=200)
        pipette.drop_tip()
        
        # (24)
        magdeck.engage(offset=md_offset)
        pipette.delay(seconds=engage_wait_time)
        
        # (26) Discard 100ul
        pipette.transfer(100, md_well, liquid_trash.wells('A1'))
        
        # (27) Repeat


    for i in range(2,4):

        # (28,29) Transfer 50ul NOOH to magdeck
        pipette.pick_up_tip()
        pipette.transfer(50, samples.wells('D3'), md_well, new_tip='never')
        
        # (30)
        magdeck.disengage()
        pipette.set_flow_rate(aspirate=50, dispense=50)
        pipette.mix(5, 50, md_well)
        pipette.set_flow_rate(aspirate=200, dispense=200)
        pipette.drop_tip()
        
        # (31) Incubate for 4m
        pipette.move_to(md_well)
        pipette.delay(minutes=1) # 4m TODO
        
        # (32)
        magdeck.engage(offset=md_offset)
        pipette.delay(seconds=engage_wait_time)
        
        # (33) Store 50ul at 4ºC in well Ai
        pipette.transfer(50, md_well, td_lab.wells(f'A{i}'))
        pipette.blow_out(td_lab.wells(f'A{i}'))
        
        # (34) Repeat

    # (35,36) Transfer 200ul ammonia to magdeck
    pipette.pick_up_tip()
    pipette.transfer(200, samples.wells('D4'), md_well, new_tip='never')

    # Incubar a 60ºC: parar ninja, transferir samples, iniciar ninja
    thermocycler.send_command('stop')
    sleep(5)
    status = thermocycler.get_status()
    if status['lid_closed'] == 0:
        pipette.distribute(100, md_well, tc_lab.wells('A2', 'A3'))
    else:
        raise Exception("Could not open thermocycler lid. Stopping")
    pipette.drop_tip()
    thermocycler.send_command('start', program = HEAT_PROGRAM)
    
    # (37)
    magdeck.disengage()
    
    # (38) Incubate for 10m
    pipette.delay(minutes=10) # 10m TODO

    
    # (39) Transfer beads to MagDeck and engage
    thermocycler.send_command('stop')
    sleep(5)
    pipette.consolidate(100, tc_lab.wells('A2', 'A3'), md_well)
    magdeck.engage(offset=md_offset)
    pipette.delay(seconds=engage_wait_time)
    
    # (40) Discard 200ul
    pipette.transfer(200, md_well, liquid_trash.wells('A1'))
    
    # (41,42) Transfer 300ul buffer nº3 beads to magdeck
    pipette.transfer(300, samples.wells('D5'), md_well)
    
    # (43)
    magdeck.disengage()
    
    # (44) Store 300ul at 4ºC
    pipette.transfer(300, md_well, td_lab.wells('A4'))
    pipette.blow_out(td_lab.wells('A4'))

    '''




def separate_test(magdeck, thermocycler, md_lab, td_lab, tc_lab, samples, tiprack, liquid_trash, pipette, md_well, n_well, md_offset, engage_wait_time, plunger_speeds, primers):

    # Inner functions: mix, engage, stop thermocycler and clean

    def engage():
        magdeck.engage(offset=md_offset)
        pipette.delay(seconds=engage_wait_time)
    
    def mix(well=md_lab.wells('A1')):
        pipette.set_flow_rate(aspirate=plunger_speeds['aspirate_mix'],
                              dispense=plunger_speeds['dispense_mix'])
        pipette.mix(3, 150, well)
        pipette.set_flow_rate(aspirate=plunger_speeds['aspirate_normal'],
                              dispense=plunger_speeds['dispense_normal'])

    def stop_thermocycler():
        # Returns True if the lid is open, False otherwise
        thermocycler.send_command('stop')
        sleep(5)
        status = thermocycler.get_status()
        return status['lid_closed'] == 0
        

    def clean(times, buffer_well, volume):

        for i in range(1,times+1):

            # Transfer another to magdeck
            pipette.pick_up_tip()
            pipette.transfer(volume, buffer_well, md_well, new_tip='never')
            
            # Mix
            magdeck.disengage()
            mix()
            pipette.drop_tip()
            
            # Engage magdeck
            engage()
            
            # (26) Discard buffer
            pipette.transfer(volume, md_well, liquid_trash.wells('A1'))
            
            # (27) Repeat
    

    
    # -------------- Start -----------------        
    

    #thermocycler.connect()

    # Prepare thermocycler: heat to 60º
    #thermocycler.send_command('start', program = HEAT_PROGRAM)
    
    pipette.set_flow_rate(aspirate=plunger_speeds['aspirate_normal'],
                          dispense=plunger_speeds['dispense_normal'])

    # (1) Mix beads in thermal module
    pipette.pick_up_tip()
    mix()
    
    # (4)
    engage()
    '''
    # (5) Store 300ul from magdeck
    pipette.transfer(300, md_well, td_lab.wells('A1'))


    
    # Repeat with 3 different dilutions
    
    for i in range(0,3):

        # Do the whole process twice, one is a control

        for j in ['A','C']:

            # Clean thrice with 0.5x SSC
            clean(3, samples.wells('D1' if j == 'A' else 'C1'), 300)
            
            # (13,14) Trasfer 0.5x SSC to magdeck
            pipette.transfer(100, samples.wells('D1'), md_well)
            
            # (15) Transfer primer mix to magdeck
            pipette.pick_up_tip()
            pipette.transfer(20, primers.wells(f'{j}{2*i+1}'), md_well, new_tip='never')
    
            # (16)
            magdeck.disengage()
            
            # (17)
            mix()
            pipette.move_to(md_well)

            # (18) Incubate and mix for 10 minutes
            pipette.delay(seconds=10)#minutes=10)
            pipette.drop_tip()
            
            # (19)
            engage()
            
            # (20) Discard 150ul
            pipette.transfer(150, md_well, liquid_trash.wells('A1'))

            # Clean twice with EDTA
            clean(2, samples.wells('D2'), 100)

            
            # (35,36) Transfer 200ul ammonium to magdeck
            pipette.pick_up_tip()
            pipette.transfer(200, samples.wells('D4'), md_well, new_tip='never')

            # Incubar a 60ºC: parar ninja, transferir samples, iniciar ninja
            if stop_thermocycler:
                pipette.distribute(100, md_well, tc_lab.wells(f'{j}{i+2}'), new_tip='never')
            else:
                raise Exception("Could not open thermocycler lid. Stopping")
            
            pipette.drop_tip()
            thermocycler.send_command('start', program = HEAT_PROGRAM)
    
            # (37)
            magdeck.disengage()
            
            # (38) Incubate for 10m
            pipette.delay(seconds=10)#minutes=10)

            # (39) Transfer beads to MagDeck and engage
            if stop_thermocycler:
                pipette.consolidate(100, tc_lab.wells(f'{j}{i+2}'), md_well)
            else:
                raise Exception("Could not open thermocycler lid. Stopping")
            
            engage()
            
            # (40) Store 200ul
            pipette.transfer(200, md_well, td_lab.wells(f'{j}{i+2}'))

    '''
            



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
magdeck       = modules.load('MagDeck', slot=4)
md_lab        = labware.load(magdeck_plate, slot=4, share=True)
# TODO: LOAD ACTUAL LABWARE WITH CORRECT MEASURES AND MAGDECK ENGAGE HEIGHT


# Thermal module. SHOULD REMAIN AT 4ºC DURING THE WHOLE PROTOCOL. TODO
tempdeck      = NinjaTempDeck(slot=1, simulating = True)
td_lab        = tempdeck.labware

# Thermocycler. Same as above. TODO
thermocycler  = NinjaPCR(slot=10, simulating = robot.is_simulating())
tc_lab        = thermocycler.labware

samples       = labware.load('Eppendorf_Samples', slot=8)
tiprack       = labware.load('opentrons-tiprack-300ul', slot=6)
tiprack2      = labware.load('opentrons-tiprack-300ul', slot=3)
liquid_trash  = labware.load('corning_384_wellplate_112ul_flat', slot = 5)
primers       = labware.load('eppendorf_rack', slot=2)

pipette_l     = instruments.P300_Single(mount='left', tip_racks=[tiprack])#, tiprack2])


md_well = md_lab.wells('A1')
n_well  = tc_lab.wells('A1')
md_offset = 0
engage_wait_time = 10
plunger_speeds = {'aspirate_mix': 300, 'dispense_mix': 300, 'aspirate_normal': 150, 'dispense_normal': 150}

args = [magdeck, thermocycler, md_lab, td_lab, tc_lab, samples, tiprack, liquid_trash, pipette_l, md_well, n_well, md_offset, engage_wait_time, plunger_speeds, primers]

separate_test(*args)
