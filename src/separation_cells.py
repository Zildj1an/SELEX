'''
Separate cells (Laura)

'''
from opentrons import labware, instruments, modules, robot
from time import sleep
from opentrons.system import nmcli
import requests, logging, time
from abc import ABC





STOPPED_STR = "stopped";
LIDWAIT_STR = "lidwait";
RUNNING_STR = "running";
COMPLETE_STR = "complete";
STARTUP_STR = "startup";
ERROR_STR = "error";
PAUSED_STR = "paused";

PCR_NAME = "NinjaPCR"
TEMPDECK_NAME = "NinjaTempDeck"
    
CONNECTION_MODES = ["external_wifi", "ninja_ap", "opentrons_ap"]
    
COMMAND_DIR = "/command"

STATUS_DIR = "/status"

SAMPLE_PROGRAM = {'name': 'Sample program',
                  'lid_temp': 110,
                  'steps': [
                      {'type': 'step',
                       'time': 150,
                       'temp': 95,
                       'name': 'Initial Step',
                       'ramp': 0},
                      {'type': 'cycle',
                       'count': 15,
                       'steps': [
                           {'type': 'step',
                            'time': 30,
                            'temp': 95,
                            'name': 'Denaturing',
                            'ramp': 0},
                           {'type': 'step',
                            'time': 30,
                            'temp': 53.5,
                            'name': 'Annealing',
                            'ramp': 0},
                           {'type': 'step',
                            'time': 30,
                            'temp': 72,
                            'name': 'Extending',
                            'ramp': 0}
                       ]},
                      {'type': 'step',
                       'time': 180,
                       'temp': 72,
                       'name': 'Final Extension',
                       'ramp': 0},
                      {'type': 'step',
                         'time': 54000,
                         'temp': 20,
                         'name': 'Final Hold',
                         'ramp': 0}]}
                      
"""
Abstract base class for all NinjaPCR-based modules (thermocycler, thermal modules)
"""
class NinjaModule(ABC):

    def __init__(self,
                 simulating = True,
                 slot = '10',
                 name = 'ninjapcr',
                 connection_mode = 'external_wifi',
                 ssid = None,
                 psk = None,
                 lw_name = None):

        if connection_mode not in CONNECTION_MODES:
            raise ValueError(f'Invalid connection mode: {connection_mode}')

        self.simulating = simulating
        self.local_url = f'http://{name}.local'
        self.net_ssid = ssid
        self.net_psk = psk
        self.connected = False
        self.connection_mode = connection_mode
        
        # Define and load associated labware

        if lw_name not in labware.list():
            labware.create(
                lw_name,                        # Labware Name
                grid=(4, 4),                    # Amount of (columns, rows)
                spacing=(9, 9),                 # Distances (mm) between each (column, row)
                diameter=2,                     # Diameter (mm) of each well on the plate
                depth=20,                       # Depth (mm) of each well on the plate
                volume=50)

        self.labware = labware.load(lw_name, slot=slot)


    def get_status(self):

        if self.simulating:
            return {'simulating': True}

        # Get status as dictionary

        response = requests.get(self.local_url + STATUS_DIR)

        status = {}
        
        if response and response.status_code == 200:
            # We got a response
            json = {k:v for k,v in [x.split('=') for x in response.text[23:-6].split('&')]}
            status['state'] = json['s']
            status['program_id'] = json['d']
            status['lid_temp'] = json['l']
            status['base_temp'] = json['b']
            status['thermocycler_state'] = json['t']
            status['sample_temp'] = json['z']
            status['lid_closed'] = json['L']

            if status['state'] == RUNNING_STR:
                status['elapsed_time'] = json['e']
                status['remaining_time'] = json['r']
            
            
        else:
            self.connected = False
            raise Exception(f'Bad connection: {response.status_code}')

        return status

    

    def send_command(self, cmd, program = None):

        if self.simulating:
            return

        # Send an HTTP API request to the NinjaPCR with the given command
        # When cmd == 'start', a program in dict form must be specified

        if not self.connected:
            raise Exception('NinjaPCR is not connected')
        

        params = self._build_params(cmd, program)

        response = requests.get(self.local_url + COMMAND_DIR, params=params)

        if response and response.status_code == 200:
            # We got a response
            #if '"1"' not in response.text:
                # Unsuccesful command
            #    raise Exception(f'Could not execute command {cmd}')
            log.info(f'Sent command {cmd}')
                            
        else:
            self.connected = False
            raise Exception(f'Bad connection: {response.status_code}')

        

    def _build_params(self, cmd, program):

        # Prepare the parameters for the HTTP API request

        params = {'s': 'ACGTC',
                  'c': cmd}

        if cmd == 'start':
            params['l'] = program['lid_temp']

            # Build program string

            prog_string = ""

            for i in range(len(program['steps'])):

                p = program['steps'][i]
                
                if p['type'] == 'step':
                    # If this is a step, add (1..) when necessary and build string
                    if i == 0 or program['steps'][i-1]['type'] == 'cycle':
                        prog_string += f'(1{self._build_step_string(p)})'
                    else:
                        prog_string += f'{self._build_step_string(p)}'

                else:
                    # If this is a cycle, just build it

                    prog_string += self._build_step_string(p)

            params['p'] = prog_string
                    
        return params

    def _build_step_string(self, program):
        
        # Build the command string for this step

        step_string = ""

        if program['type'] == 'step':
            p = program
            step_string = f'[{p["time"]}|{p["temp"]}|{p["name"]}|{p["ramp"]}]'

        else:
            step_string = f'({program["count"]}'
            for s in program['steps']:
                step_string += f'[{s["time"]}|{s["temp"]}|{s["name"]}|{s["ramp"]}]'
            step_string += ')'

        return step_string

    
    def connect(self):
        # Attempt to connect to the NinjaPCR. This should be called before attempting to send any command
        if self.simulating:
            self.connected = True
            return
        
        if self.connection_mode == 'ninja_ap':
            self._connect_to_ap()
            
        elif self.connection_mode == 'opentrons_ap':
            self._setup_ap()

        self._check_connection()
        self.connected = True

    def _check_connection(self):
        # Test HTTP connection
        
        response = requests.get(self.local_url)
        if response and response.status_code == 200:
            log.info(f'Connected to NinjaPCR at {self.local_url}')
        else:
            raise Exception(f'Could not connect to NinjaPCR at {self.local_url}. Status code: {response.status_code}')

        
    def _connect_to_ap(self):
        
        # Connect to the NinjaPCR AP
    
        if not nmcli.connection_exists(self.ssid):
            if self.ssid not in nmcli.available_ssids():
                raise Exception(f'Network {self.ssid} not found')
                            
            success, msg = nmcli.configure(self.ssid, nmcli.WPA_PSK, self.psk)
            if not success:
                raise Exception(f'Could not setup connection: {msg}')
                            
            sleep(2)
            if not nmcli.connection_exists(self.ssid):
                raise Exception('Could not connect to ssid {self.ssid}. Wrong passphrase?')
            
            
    def _setup_ap(self):

        raise NotImplementedError()

        # Setup the robot's wifi interface as an access point

        nmcli._call(['nmcli', 'dev', 'wifi', 'hotspot', 'ifname', 'wlan0', 'ssid', self.ssid, 'password', self.psk])


        
    
"""
Opentrons driver for NinjaPCR thermocycler
""" 
class NinjaPCR(NinjaModule):

    def __init__(self,
                 simulating = True,
                 slot = '10',
                 name = 'ninjapcr',
                 connection_mode = 'external_wifi',
                 ssid = None,
                 psk = None):

        NinjaModule.__init__(self, simulating, slot, name, connection_mode, ssid, psk, PCR_NAME)

        

    def wait_for_program(self, program):

        if self.simulating:
            return
            
        # Starts a program and actively waits until it's finished

        self.send_command('start', program)

        sleep(5)

        status = self.get_status()

        if status['state'] in [LIDWAIT_STR, RUNNING_STR]:
            log.info(f'NinjaPCR was successfully started and is in state {status["state"]}')
            keep_going = True
        else:
            log.info(f'NinjaPCR did nos start successfully. State: {status["state"]}')
            keep_going = False
        
        while keep_going:
            sleep(5)
            status = self.get_status()
            if status['state'] in [STOPPED_STR, COMPLETE_STR, ERROR_STR]:
                log.info(f'NinjaPCR stopped in state {status["state"]}')
                if status['state'] == ERROR_STR:
                    raise Exception("NinjaPCR error")
                keep_going = False
            elif status['state'] == RUNNING_STR:
                log.info(f'NinjaPCR is running. Remaining time: {status["remaining_time"]}')
                

"""
Opentrons driver for NinjaPCR-based TempDeck
"""
class NinjaTempDeck(NinjaModule):

    def __init__(self,
                 simulating = True,
                 slot = '10',
                 name = 'ninjapcr',
                 connection_mode = 'external_wifi',
                 ssid = None,
                 psk = None):
    
        self.target = None
        NinjaModule.__init__(self, simulating, slot, name, connection_mode, ssid, psk, TEMPDECK_NAME)
        
    
    def get_temp(self):

        if self.simulating:
            return 0

        status = self.get_status()

        return status['sample_temp']
    
        
    def set_temp(self, temp, lid_temp=110):

        if self.simulating:
            return

        self.target = temp

        program = {'name': 'Constant temp',
                      'lid_temp': lid_temp,
                      'steps': [
                          {'type': 'step',
                           'time': 86400,
                           'temp': temp,
                           'name': 'Final Hold',
                           'ramp': 0},
                      ]}
        
        self.send_command('start', program = program)
        

    def wait_for_temp(self):

        if self.simulating:
            return

        while(self.get_temp() - self.target > 1):
            sleep(5)
        

    def deactivate():

        if self.simulating:
            return

        self.send_command('stop')
        self.target = None

# FUNCTIONS ························································································

"""
Opentrons driver for NinjaPCR-based TempDeck

"""
class NinjaTempDeck(NinjaModule):

    def __init__(self,
                 simulating = True,
                 slot = '10',
                 name = 'ninjapcr',
                 connection_mode = 'external_wifi',
                 ssid = None,
                 psk = None):

        self.target = None
        NinjaModule.__init__(self, simulating, slot, name, connection_mode, ssid, psk, TEMPDECK_NAME)

    def get_temp(self):

        if self.simulating:
            return 0

        status = self.get_status()

        return status['sample_temp']
    def set_temp(self, temp, lid_temp=110):

        if self.simulating:
            return

        self.target = temp

        program = {'name': 'Constant temp',
                      'lid_temp': lid_temp,
                      'steps': [
                          {'type': 'step',
                           'time': 86400,
                           'temp': temp,
                           'name': 'Final Hold',
                           'ramp': 0},
                      ]}
        self.send_command('start', program = program)

    def wait_for_temp(self):

        if self.simulating:
            return

        while(self.get_temp() - self.target > 1):
            sleep(5)

    def deactivate():

        if self.simulating:
            return

        self.send_command('stop')
        self.target = None













metadata = {
   'protocolName' : 'Separation of cells',
   'description'  : 'Separation of cells',
   'source'       : 'https://github.com/Zildj1an/SELEX'
}

plate_eppendorf = 'Eppendorf_Samples'
if plate_eppendorf not in labware.list():
   Eppendorf = labware.create(
      plate_eppendorf,
      grid = (8,4),
      spacing = (15,20),
      diameter = 10,
      depth  = 35,
      volume = 100)

# FUNCTIONS ························································································

def robot_wait():

    if not robot.is_simulating():
       robot.comment("Waiting...")
       robot._driver.turn_on_red_button_light()
       while not robot._driver.read_button():
          sleep(0.5)

       robot._driver.turn_on_blue_button_light()

def incubate(mins, secs=0, ar=100, dr=100):
    
   duration = 60*mins + secs
   start_time = time.perf_counter()
   elapsed_time = 0
   while elapsed_time < duration:
      
      pipette.set_flow_rate(aspirate=ar, dispense=dr)
      pipette.pick_up_tip()
      pipette.mix(2,100,md_lab.wells('A1'))
      pipette.drop_tip()
      pipette.pick_up_tip()
      pipette.mix(2,100,md_lab.wells('A2'))
      pipette.delay(seconds=15)
      pipette.drop_tip()

      if robot.is_simulating():
          elapsed_time += 30
      else:
          elapsed_time = time.perf_counter() - start_time

def custom_pick(quantity, from_w, to_w, blow_out=False, reuse_tip=False, mix_after=False, mix_before=False, mix_asp_rate=100, mix_dis_rate=100, tr_asp_rate=100, tr_dis_rate=100, mix_after_params=(3,100)):

   if not reuse_tip:
      pipette.pick_up_tip()
   if mix_before:
      pipette.set_flow_rate(aspirate=mix_asp_rate, dispense=mix_dis_rate)
      pipette.mix(3,100,from_w)
   pipette.set_flow_rate(aspirate=tr_asp_rate, dispense=tr_dis_rate)
   pipette.transfer(quantity, from_w,to_w, new_tip='never')
   if mix_after:
      pipette.set_flow_rate(aspirate=mix_asp_rate, dispense=mix_dis_rate)
      pipette.mix(mix_after_params[0],mix_after_params[1],to_w)
   if blow_out:
      pipette.blow_out(to_w)
   if not reuse_tip:
      pipette.drop_tip()

# Labware
magdeck_plate='MagDeck_24'

magdeck          = modules.load('MagDeck',           slot=4)
md_lab           = labware.load(magdeck_plate,       slot=4, share=True)
tiprack          = labware.load('opentrons-tiprack-300ul', slot=6)
tiprack2         = labware.load('opentrons-tiprack-300ul', slot=11)
tiprack3         = labware.load('opentrons-tiprack-300ul', slot=9)
tiprack_m        = labware.load('opentrons-tiprack-10ul', slot=8)
trash_liquid     = labware.load('corning_384_wellplate_112ul_flat', slot = 3)
samples          = labware.load('Eppendorf_Samples', slot=7)
samples2         = labware.load('96-flat', slot=5)
tempdeck         = NinjaTempDeck(slot=1, simulating = True)
td_lab           = tempdeck.labware

# Pipette
pipette          = instruments.P300_Single(mount='left', tip_racks=[tiprack, tiprack2, tiprack3])
pipette_multi    = instruments.P50_Multi(mount='right', tip_racks=[tiprack_m])

modules.magdeck.LABWARE_ENGAGE_HEIGHT[magdeck_plate] = 30


# START RUN ························································································

pipette.set_flow_rate(aspirate=15,dispense=15)
robot._driver.turn_on_rail_lights()
#tempdeck.set_temp(temp=4)

# (-1) Move 100ul from A3 to each of the magdeck
rates={'mix_asp_rate':300, 'mix_dis_rate':300, 'tr_asp_rate':300, 'tr_dis_rate':300}
pipette.pick_up_tip()
custom_pick(100, td_lab.wells('A1'), md_lab.wells('A1'), blow_out=True, reuse_tip=True, mix_before=True, **rates)
custom_pick(100, td_lab.wells('A1'), md_lab.wells('A2'), blow_out=True, reuse_tip=True, mix_before=True, **rates)
pipette.drop_tip()

# (0) Remove liquid beads
rates['tr_asp_rate'] = 15
magdeck.engage()
pipette.delay(minutes=2)
pipette.pick_up_tip()
custom_pick(100, md_lab.wells('A1'), samples.wells('A3'), blow_out=True, reuse_tip=True, **rates)
custom_pick(100, md_lab.wells('A2'), samples.wells('A3'), blow_out=True, reuse_tip=True, **rates)
pipette.drop_tip()
magdeck.disengage()

# (1) Add 700 ul from A1,A2 to magdeck
custom_pick(700, samples.wells('A1'), md_lab.wells('A1'),blow_out=True,mix_before=True)
custom_pick(700, samples.wells('A2'), md_lab.wells('A2'),blow_out=True,mix_before=True)

# (2) 10 min incubate
incubate(10)

# (3) Engage 2 mins
magdeck.engage()
pipette.delay(minutes=2)
amount = 700
p1 = 1
p2 = 2

for x in range(1,5):

    if x > 1:
      amount = 400
      p1 = 3
      p2 = 4

    # (4) Move amount from A1,A2 to B1,B2
    custom_pick(amount, md_lab.wells('A1'), samples.wells('B' + str(p1)), blow_out=True, **rates)
    custom_pick(amount, md_lab.wells('A2'), samples.wells('B' + str(p2)), blow_out=True, **rates)
    magdeck.disengage()

    if x < 4:

       # (5) Move 400ul of PBS to A1,A2
       pipette.delay(seconds=15)
       custom_pick(400, samples.wells('A4'), md_lab.wells('A1'),blow_out=True,mix_after=True)
       custom_pick(400, samples.wells('A5'), md_lab.wells('A2'),blow_out=True,mix_after=True)

       # (6) Engage 2 mins
       magdeck.engage()
       pipette.delay(minutes=2)

# (7) Elution, move 100ul of elution buffer A6 to A1,A2
pipette.delay(seconds=20)
custom_pick(100, samples.wells('A6'), md_lab.wells('A1'),blow_out=True, mix_after=True)
custom_pick(100, samples.wells('A6'), md_lab.wells('A2'),blow_out=True, mix_after=True)
incubate(5)

# (8) Engage 1 mins
magdeck.engage()
pipette.delay(minutes=1)

# (9) Move 100ul from A1,A2 to C1,C2
custom_pick(100, md_lab.wells('A1'), samples.wells('C1'), blow_out=True, **rates)
custom_pick(100, md_lab.wells('A2'), samples.wells('C2'), blow_out=True, **rates)
magdeck.disengage()

# (10) Move 100ul from  A7 eppendorf to A1,A2
pipette.pick_up_tip()
custom_pick(100, samples.wells('A7'), md_lab.wells('A1'),blow_out=True,mix_after=True, reuse_tip=True)
custom_pick(100, md_lab.wells('A1'), samples2.wells('D1'),blow_out=True, reuse_tip=True)
pipette.drop_tip()
pipette.pick_up_tip()
custom_pick(100, samples.wells('A7'), md_lab.wells('A2'),blow_out=True,mix_after=True, reuse_tip=True)
custom_pick(100, md_lab.wells('A2'), samples2.wells('D2'),blow_out=True, reuse_tip=True)
pipette.drop_tip()


for pos in ['A','B','C']:

    custom_pick(100,samples.wells(pos+str(1)),samples2.wells(pos + str(1)),blow_out=True,mix_before=True)
    custom_pick(100,samples.wells(pos+str(2)),samples2.wells(pos + str(2)),blow_out=True,mix_before=True)

custom_pick(100,samples.wells('B3'),samples2.wells('E1'),blow_out=True,mix_before=True)
custom_pick(100,samples.wells('B4'),samples2.wells('E2'),blow_out=True,mix_before=True)


# Dilution

pipette_multi.set_flow_rate(aspirate=100, dispense=100)
pipette_multi.pick_up_tip()
for i in range(1,10,2):
    pipette_multi.transfer(50, samples2.wells(f'A{i}'), samples2.wells(f'A{i+2}'), blow_out=True, mix_before=(2,50), new_tip='never')
pipette_multi.mix(2,50,samples2.wells('A11'))
pipette_multi.drop_tip()

pipette_multi.pick_up_tip()
for i in range(2,11,2):
    pipette_multi.transfer(50, samples2.wells(f'A{i}'), samples2.wells(f'A{i+2}'), blow_out=True, mix_before=(2,50), new_tip='never')
pipette_multi.mix(2,50,samples2.wells('A12'))
pipette_multi.drop_tip()



'''
for pos in ['C','D','A','B','E']:

    pos1 = 1
    pos2 = 2

    for x in range(1,6):
       if pos != 'D' or x < 2: 
          pipette.pick_up_tip()
          custom_pick(100,samples2.wells(pos+str(pos1)),samples2.wells(pos + str(pos1 + 2)),blow_out=True, reuse_tip=True,mix_after=True)
          pos1 = pos1 + 2
          pipette.drop_tip()

    for x in range(1,6):
       if pos != 'D' or x < 2: 
         pipette.pick_up_tip()
         custom_pick(100,samples2.wells(pos+str(pos2)),samples2.wells(pos + str(pos2 + 2)),blow_out=True,reuse_tip=True,mix_after=True)
         pos2 = pos2 + 2
         pipette.drop_tip()
'''
robot._driver.turn_off_rail_lights()

