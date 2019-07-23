'''
 Amplify the DNA via PCR

'''

from opentrons import labware, instruments, modules


def amplify_DNA(plates = "{}", pipette_r, thermocycler):

        pipette_r.pick_up_tip()

        quantity = {"20","10","20"}

        # (1) Aptamers to PCR

        for x,y in [('E1','A1'),('E2','A2'),('E3','A3'),('E4','A4')]:

         	# Aspirate 4
                pipette_r.aspirate(quantity[0],plates[0].wells(x))
	        # Dispense 4
                pipette_r.dispense(quantity[0],thermocycler.wells(y))

        # (2) Primers to PCR

        for x,y in [('E1','A1'),('E2','A2'),('E3','A3'),('E4','A4')]:

         	# Aspirate 4
                pipette_r.aspirate(quantity[1],plates[1].wells(x))
	        # Dispense 4

                pipette_r.dispense(quantity[1],thermocycler.wells(y))

        # (3) 

        for x,y in [('E1','A1'),('E2','A2'),('E3','A3'),('E4','A4')]:

         	# Aspirate 4
                pipette_r.aspirate(quantity[2],plates[2].wells(x))
	        # Dispense 4
                pipette_r.dispense(quantity[2],thermocycler.wells(y))


        pipette_r.drop_tip()

