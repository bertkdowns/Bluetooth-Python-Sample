import sys
sys.path.insert(0,"/home/pi/heatpumpdryer-data-collection/openapi")

from PyP100 import PyP110
from bluepy.btle import Scanner, DefaultDelegate
from ela.bluetooth.advertising.TagFactory import Tagfactory
from dotenv import load_dotenv
from ahuora.flowsheet import Flowsheet
import openapi_client
import os
import time

load_dotenv()

sensor_locations = {
    "P RHT 904C92": {
        "label": "Air-Dryer_out-Evap-in",
        "unitop": "evap_air_in",
        "propkey": "PROP_MS_0", # Temperature, used but not relevant
    },
    "P RHT 904C90": {
        "label": "Air-Cond_out-Dryer_in",
        "unitop": "cond_air_out_live",
        "propkey": "PROP_MS_0", # Cold Fluid (air) Outlet Temperature, Not Used (depends on the stream)
    },
    "P TPROBE 0021F9": { 
        "label": "Air-Evap_out-Cond_in",
        "unitop": "evap_air_out_live",
        "propkey": "PROP_MS_0", # Hot Fluid (air) Outlet Temperature, not used but stored (depends on stream)
    },
    "P TPROBE 0021F8": {
        "label": "Prop-Compressor_out-Cond_in",
        "unitop": "compressor",
        "propkey": "OUTLET_TEMPERATURE", # Compressor Outlet Temperature, used as a calculation mode.
    },
    # "P TPROBE 0021F7": {
    #     "label": "Prop-Evap_out-Compressor_in",
    #     "unitop": "evap_prop_out", # input/output of recycle, tear guess. could also be set to evap cold stream outlet temp
    #     "propkey": "PROP_MS_0",
    # },
    "P TPROBE 0021F7": {
        "label": "Prop-Evap_out-Compressor_in",
        "unitop": "evaporator", # input/output of recycle, tear guess. could also be set to evap cold stream outlet temp
        "propkey": "PROP_HX_3", # cold fluid outlet temperature, used as a calculation mode
    },
    "Energy": {
        "label": "Total Power",
        "unitop": "power_required",
        "propkey": "PROP_MS_3", # Power Required, not used. Stored in a material stream for now ;)
    },
}

# ----------------- Flowsheet Setup --------------------

configuration = openapi_client.Configuration(
    host = "http://localhost:8001"
)
FS_ID = 6
api = Flowsheet(configuration,FS_ID)

for key, value in sensor_locations.items():
    sensor_locations[key]["id"] = api.get_property_id(value["unitop"],value["propkey"])


# ---------------- BLUETOOTH SETUP --------------------

## 
# @class ScanDelegate
# @brief scan delegate to catch and interpret bluetooth advertising events
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            pass
            # this gets called a lot every scan, not sure if that's bad
            #print("Discovered device", dev.addr)
        elif isNewData:
            print("Received new data from", dev.addr)

## associate the delegate to the scanner and start it for 10.0 seconds
scanner = Scanner().withDelegate(ScanDelegate())

# ------------- Tapo Power Plug Setup ----------------------

p110 = PyP110.P110(os.getenv("TAPO_IP"), os.getenv("TAPO_ACCOUNT"), os.getenv("TAPO_PASSWORD")) 

p110.handshake() #Creates the cookies required for further methods
p110.login() #Sends credentials to the plug and creates AES Key and IV for further methods

#The P110 has all the same basic functions as the plugs and additionally allow for energy monitoring.
# print(p110.getEnergyUsage()) #Returns dict with all of the energy usage of the connected plu
#{'today_runtime': 27, 'month_runtime': 27, 'today_energy': 2, 'month_energy': 2, 'local_time': '2024-05-15 12:28:35', 'electricity_charge': [0, 0, 0], 'current_power': 1601933}
# -------------- MAIN LOOP ------------------------------
while True:
    print("Scanning")
    devices = scanner.scan(5.0)

    # ----------------- DATA PROCESSING ------------------

    ## display result get from scanner
    for dev in devices:
        if( isinstance(dev.rawData, bytes)):
            tag = Tagfactory.getInstance().getTag(dev.rawData)
            
            # skip devices that aren't ELA tags
            if(tag.formattedDataSensor == "VOID"):
                continue
            
            # Find the tag name
            name = "UNNAMED"
            for (adtype, desc, value) in dev.getScanData():
                if(desc == "Complete Local Name"):
                    name = value
            
            #print("Device %s (%s), RSSI=%d dB, Interpreted ELA Data=%s, RawData=%s" % (dev.addr, dev.addrType, dev.rssi, Tagfactory.getInstance().getTag(dev.rawData).formattedDataSensor ,binascii.b2a_hex(dev.rawData).decode('ascii')))
            
            # write the data to the db
            for measurement, value in tag.fields().items():
                if measurement != "temperature":
                    continue # don't write humidity, only temperature
                
                if(name not in sensor_locations):
                    print(name + " not registered as a location, skipping")
                    continue
                location = sensor_locations[name]
                if location["id"] is None:
                    print("Could not find a propkey")
                    continue
                print("%s: writing %s:%s to %s : %s" % (name,measurement,value,location["unitop"], location["id"]))
                api.update_property(location["id"], str(value))
    
    # Print the info from the tapo plug
    try:
        energy = p110.getEnergyUsage()
        location = sensor_locations["Energy"]
        print("Writing Energy:",energy["current_power"], ": ", location["id"])
        api.update_property(location["id"], str(energy["current_power"]))
    except Exception as e:
        print("failed to get Energy data")
    print("solving")
    api.solve()
    print("done.")
    time.sleep(30)
