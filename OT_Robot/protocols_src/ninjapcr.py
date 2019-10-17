from opentrons import labware
from opentrons.system import nmcli
import requests, logging
from time import sleep
from abc import ABC

log = logging.getLogger('opentrons')

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
