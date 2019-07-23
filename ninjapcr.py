from opentrons import labware
from opentrons.system import nmcli
import requests, logging
from time import sleep

log = logging.getLogger('opentrons')

PCR_NAME = "NinjaPCR"
    
CONNECTION_MODES = ["external_wifi", "ninja_ap", "opentrons_ap"]
    
COMMAND_DIR = "/command"

SAMPLE_PROGRAM = {'name': 'Sample program',
                  'lid_temp': 110,
                  'steps': [
                      {'type': 'step',
                       'time': 30,
                       'temp': 95,
                       'name': 'Initial Step',
                       'ramp': 0},
                      {'type': 'cycle',
                       'count': 2,
                       'steps': [
                           {'type': 'step',
                            'time': 30,
                            'temp': 95,
                            'name': 'Denaturing',
                            'ramp': 0},
                           {'type': 'step',
                            'time': 30,
                            'temp': 55,
                            'name': 'Annealing',
                            'ramp': 0},
                           {'type': 'step',
                            'time': 60,
                            'temp': 72,
                            'name': 'Extending',
                            'ramp': 0}
                       ]},
                      {'type': 'step',
                       'time': 0,
                       'temp': 20,
                       'name': 'Final Hold',
                       'ramp': 0}
                      ]}

def NinjaPCR(Object):

    """
    Opentrons driver for NinjaPCR
    """

    def __init__(self,
                 slot = "10",
                 name = "ninjapcr",
                 connection_mode = "external_wifi",
                 ssid = None,
                 psk = None):

        if connection_mode not in CONNECTION_MODES:
            raise ValueError("Invalid connection mode: {}".format(connection_mode))

        self.local_url = "http://" + name + ".local"
        self.net_ssid = ssid
        self.net_psk = psk
        self.connected = False
        
        # Define and load associated labware
        
        wells = labware.create(
            PCR_NAME,                       # Labware Name
            grid=(4, 4),                    # Amount of (columns, rows)
            spacing=(9, 9),                 # Distances (mm) between each (column, row)
            diameter=2,                     # Diameter (mm) of each well on the plate
            depth=10,                       # Depth (mm) of each well on the plate
            volume=50)
        
        labware.load(pcr_name, slot = slot)


    def send_command(self, cmd, program = None):

        # Send an HTTP API request to the NinjaPCR with the given command
        # When cmd == 'start', a program in dict form must be specified

        if not self.connected:
            raise Error('NinjaPCR is not connected')
        

        params = self._build_params(cmd, program)

        response = requests.get(self.local_url + COMMAND_DIR, params=params)

        if response and response.status_code == 200:
            # We got a response
            if '"1"' not in response.text:
                # Unsuccesful command
                raise Error(f'Could not execute command {cmd}'

        else:
            raise Error(f'Bad connection: {response.status_code}')
        


    def _build_params(self, cmd, program):

        # Prepare the parameters for the HTTP API request

        params = {'s': 'ACGTC',
                  'c': cmd}

        if cmd == "start":
            params['l'] = program['lid_temp']

            # Build program string

            prog_string = ""

            for i in range(len(program['steps'])):

                p = program['steps'][i]
                
                if p['type'] == 'step':
                    # If this is a step, add (1..) when necessary and build string
                    if i == 0 or program['steps'][i-1]['type'] == 'cycle':
                        prog_string += '(1{})'
                    else:
                        prog_string += '{}'

                    prog_string.format(self._build_step_string(p))

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
            step_string = '[{}|{}|{}|{}]'.format(p['time'], p['temp'], p['name'], p['ramp'])

        else:
            step_string = '({}'.format(program['count'])
            for s in program['steps']:
                step_string += "[{}|{}|{}|{}]".format(s['time'], s['temp'], s['name'], s['ramp'])
            step_string += ')'

        return step_string

    
    def connect(self):
        # Attempt to connect to the NinjaPCR. This should be called before attempting to send any command
        
        if connection_mode == "ninja_ap":
            self._connect_to_ap()
            
        elif connection_mode == "opentrons_ap":
            self._setup_ap()

        self._check_connection()
        self.connected = True

    def _check_connection(self):
        # Test HTTP connection
        
        response = requests.get(self.local_url)
        if response and response.status_code == 200:
            log.info("Connected to NinjaPCR at {}".format(self.local_url))
        else:
            raise Error("Could not connect to NinjaPCR at {}. Status code: {}".format(self.local_url, response.status_code))

        
    def _connect_to_ap(self):
        
        # Connect to the NinjaPCR AP
    
        if not nmcli.connection_exists(self.ssid):
            if self.ssid not in nmcli.available_ssids():
                raise Error("Network {} not found".format(self.ssid))
                            
            success, msg = nmcli.configure(self.ssid, nmcli.WPA_PSK, self.psk)
            if not success:
                raise Error("Could not setup connection: {}".format(msg))
                            
            sleep(2)
            if not nmcli.connection_exists(self.ssid):
                raise Error("Could not connect to ssid {}. Wrong passphrase?".format(self.ssid))
            
            
    def _setup_ap(self):

        raise NotImplementedError()

        # Setup the robot's wifi interface as an access point

        nmcli._call(['nmcli', 'dev', 'wifi', 'hotspot', 'ifname', 'wlan0', 'ssid', self.ssid, 'password', self.psk]
