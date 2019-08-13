'''
Separation of the cells and aptamers
'''

from opentrons import labware, instruments, modules, robot
from ninjapcr import NinjaPCR, NinjaTempDeck

metadata = {
   'protocolName' : 'Separation',
   'description'  : 'Separation of cells and aptamers via MagDeck',
   'source'       : 'https://github.com/Zildj1an/SELEX'
}



def separate(magdeck, md_lab, td_lab, tc_lab, samples, tiprack, liquid_trash, pipette, md_well, n_well, md_offset, engage_wait_time):

    # (1) Mix beads in thermal module
    pipette.pick_up_tip()
    pipette.mix(3, 50, td_lab.wells('A1'))
    
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
        pipette.mix(3, 50, md_well)
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
    
    # (16)
    magdeck.disengage()
    
    # (17)
    pipette.mix(5, 50, md_well)
    pipette.move_to(md_well)

    # (18) Incubate and mix for 10 minutes
    for i in range(1,2): # 10m TODO
        pipette.delay(seconds=30)
        pipette.mix(1, 50, md_well)
        pipette.move_to(md_well)

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
        pipette.mix(3,50,md_well)
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
        pipette.mix(5, 50, md_well)
        pipette.drop_tip()
        
        # (31) Incubate for 4m
        pipette.move_to(md_well)
        pipette.delay(minutes=1) # 4m TODO
        
        # (32)
        magdeck.engage(offset=md_offset)
        pipette.delay(seconds=engage_wait_time)
        
        # (33) Store 50ul at 4ºC in well Ai
        pipette.transfer(50, md_well, td_lab.wells(f'A{i}'))
        
        # (34) Repeat

    # (35,36) Transfer 200ul ammonia to magdeck
    pipette.pick_up_tip()
    pipette.transfer(200, samples.wells('D4'), md_well, new_tip='never')
    
    # (37)
    magdeck.disengage()
    pipette.mix(5,50,md_well)
    pipette.drop_tip()
    
    # (38) Incubate for 10m
    pipette.move_to(md_well)
    pipette.delay(minutes=1) # 10m TODO
    
    # (39)
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



plate_eppendorf = 'Eppendorf_Samples'
if plate_eppendorf not in labware.list():
   Eppendorf = labware.create(
      plate_eppendorf,
      grid = (8,4),
      spacing = (15,20),
      diameter = 10,
      depth  = 35,
      volume = 100)

# MagDeck and associated labware
magdeck       = modules.load('MagDeck', slot=4)
md_lab        = labware.load('biorad_96_wellplate_200ul_pcr', slot=4, share=True)

# Thermal module. SHOULD REMAIN AT 4ºC DURING THE WHOLE PROTOCOL
tempdeck      = NinjaTempDeck(slot=1, simulating = True)
td_lab        = tempdeck.labware

# Thermocycler. Same as above
thermocycler  = NinjaPCR(slot=10, simulating = True)
tc_lab        = thermocycler.labware

samples       = labware.load('Eppendorf_Samples', slot=8)
tiprack       = labware.load('opentrons-tiprack-300ul', slot=6)
liquid_trash  = labware.load('corning_384_wellplate_112ul_flat', slot = 5)

pipette_l     = instruments.P300_Single(mount='left', tip_racks=[tiprack])


md_well = md_lab.wells('A1')
n_well  = tc_lab.wells('A1')
md_offset = -10.5
engage_wait_time = 10

args = [magdeck, md_lab, td_lab, tc_lab, samples, tiprack, liquid_trash, pipette_l, md_well, n_well, md_offset, engage_wait_time]

separate(*args)
