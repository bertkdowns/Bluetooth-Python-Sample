This repository is pulled from ELA-Innovation's Bluetooth-Python-sample, and then modified to support other types of sensors and sending data to influxdb.

It uses ELA-Innovations code (in the ela folder) and `bluepy` to interface with bluetooth IoT sensors. It uses the PyP100 library to interface with a Tapo P110 energy monitoring plug. The data from all these sensors is requested every 10 seconds, and then uploaded to an influxdb server.


## Usage

Requirments: Python (3.11 or later?) and InfluxDB. 

Install and start influxdb. 

Use the `.env-template` file to create a `.env` file with all the required properties.

`
pip install -r requirements.txt
`

`
python main.py
`

## Folder Structure

`/ela/` hosts the library files for interfacing with ELA sensors.

`main.py` is the actual script for gathering data.

all the other python files are just testing/example files.

