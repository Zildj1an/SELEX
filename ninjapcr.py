from opentrons import labware
from opentrons.system import nmcli
import requests, logging
from time import sleep

log = logging.getLogger('opentrons')

def NinjaPCR(Object):

    """
    Opentrons driver for NinjaPCR
    """

    PCR_NAME="NinjaPCR"
    
    CONNECTION_MODES=["external_wifi", "ninja_ap", "opentrons_ap"]
    
    def __init__(self,
                 slot="10",
                 name="ninjapcr",
                 connection_mode="external_wifi",
                 ssid="NinjaPCR"
                 psk="ninjapcr"):

        if connection_mode not in CONNECTION_MODES:
            raise ValueError("Invalid connection mode: {}".format(connection_mode))

        self.local_url = "http://" + name + ".local"
        self.net_ssid = ssid
        self.net_psk = psk
        
        # Define and load associated labware
        
        wells = labware.create(
            PCR_NAME,                       # Labware Name
            grid=(4, 4),                    # Amount of (columns, rows)
            spacing=(9, 9),                 # Distances (mm) between each (column, row)
            diameter=2,                     # Diameter (mm) of each well on the plate
            depth=10,                       # Depth (mm) of each well on the plate
            volume=50)
        
        labware.load(pcr_name, slot = slot)


    def connect(self):

        if connection_mode == "external_wifi":
            self._check_connection()

        elif connection_mode == "ninja_ap":
            self._connect_to_ap()
            
        else:

    def _check_connection(self):
        # Test HTTP connection
        
        response = requests.get(self.local_url)
        if response.status_code == 200:
            log.info("Connected to NinjaPCR at {}".format(self.local_url))
        else:
            raise Error("Could not connect to NinjaPCR at {}".format(self.local_url))

    def _connect_to_ap(self):
        # Connect to the NinjaPCR AP
        
        if nmcli.connection_exists(self.ssid):
            self._check_connection()

        else:
            success, msg = nmcli.configure(self.ssid, nmcli.WPA_PSK, self.psk)
            if not success:
                raise Error("Could not setup connection: {}".format(msg))
            sleep(2)
            if not 
            
