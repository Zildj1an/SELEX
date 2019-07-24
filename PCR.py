'''
 Amplify the DNA via PCR

'''

from opentrons import labware, instruments, modules
from ninjapcr import NinjaPCR, SAMPLE_PROGRAM


def pcr(plates = [], pipette_r, thermocycler):

        # Attempt to connect to the thermocycler

        if not thermocycler.connected:
                thermocycler.connect() 
                        
                
        pipette_r.pick_up_tip()

        volumes = ["20","10","20"]

        # (1) Aptamers to PCR

        for x,y in [('E1','A1'),('E2','A2'),('E3','A3'),('E4','A4')]:

         	# Aspirate 4
                pipette_r.aspirate(quantity[0],plates[0].wells(x))
	        # Dispense 4
                pipette_r.dispense(quantity[0],thermocycler.labware.wells(y))

        pipette_r.drop_tip()
        pipette_r.pick_up_tip()
        
        # (2) Primers to PCR

        for x,y in [('E1','A1'),('E2','A2'),('E3','A3'),('E4','A4')]:

         	# Aspirate 4
                pipette_r.aspirate(quantity[1],plates[1].wells(x))
	        # Dispense 4

                pipette_r.dispense(quantity[1],thermocycler.labware.wells(y))

        # (3) Mastermix to pcr

        pipette_r.drop_tip()
        pipette_r.pick_up_tip()
        
        for x,y in [('E1','A1'),('E2','A2'),('E3','A3'),('E4','A4')]:

         	# Aspirate 4
                pipette_r.aspirate(quantity[2],plates[2].wells(x))
	        # Dispense 4
                pipette_r.dispense(quantity[2],thermocycler.labware.wells(y))


        pipette_r.drop_tip()
        thermocycler.wait_for_program(SAMPLE_PROGRAM)
        


if __name__ == "__main__":

        # Run PCR as an independent protocol
        
        # Labware and module initialization
        
        plate = labware.load('96-flat', slot='11')
        tiprack = labware.load('tiprack-50ul', slot='6')
        ninja = NinjaPCR(slot='10')

        pipette_r = instruments.P50_Multi(mount='right', tip_racks=[tiprack])

        pcr(plates = [plate], pipette_r, ninja)
