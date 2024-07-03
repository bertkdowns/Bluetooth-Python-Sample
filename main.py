
# https://docs.influxdata.com/influxdb/v2/api-guide/client-libraries/python/
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from PyP100 import PyP110
from bluepy.btle import Scanner, DefaultDelegate
from ela.bluetooth.advertising.TagFactory import Tagfactory
from dotenv import load_dotenv
import os

load_dotenv()

sensor_locations = {
    "P RHT 904C92": "Air-Dryer_out-Evap-in",
    "P RHT 904C90": "Air-Cond_out-Dryer_in",
    "P TPROBE 0021F9": "Air-Evap_out-Cond_in",
    "P TPROBE 0021F8": "Prop-Compressor_out-Cond_in",
    "P TPROBE 0021F7": "Prop-Evap_out-Compressor_in"
}

# -------------- INFLUX DB SETUP ----------------------

bucket = os.getenv('INFLUX_BUCKET')
org = os.getenv('INFLUX_ORG')
token = os.getenv('INFLUX_TOKEN')
# Store the URL of your InfluxDB instance
url=os.getenv('INFLUX_URL')

client = influxdb_client.InfluxDBClient(
   url=url,
   token=token,
   org=org
)

write_api = client.write_api(write_options=SYNCHRONOUS)

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
                continue;
            
            # Find the tag name
            name = "UNNAMED"
            for (adtype, desc, value) in dev.getScanData():
                if(desc == "Complete Local Name"):
                    name = value
            
            #print("Device %s (%s), RSSI=%d dB, Interpreted ELA Data=%s, RawData=%s" % (dev.addr, dev.addrType, dev.rssi, Tagfactory.getInstance().getTag(dev.rawData).formattedDataSensor ,binascii.b2a_hex(dev.rawData).decode('ascii')))
            
            # write the data to the db
            for measurement, value in tag.fields().items():
                print("%s: writing %s:%s" % (name,measurement,value))
                if(name not in sensor_locations):
                    print(name + " not registered as a location, skipping")
                    continue
                location = sensor_locations[name]
                p = influxdb_client.Point(measurement).tag("name",name).tag("location",location).field("value",value)
                write_api.write(bucket=bucket, org=org, record=p)
    
    # Print the info from the tapo plug
    energy = p110.getEnergyUsage()
    p = influxdb_client.Point("current_power").tag("name","Tapo p110").tag("location","Wall Plug").field("value",energy['current_power'])
    write_api.write(bucket=bucket, org=org, record=p)