
FLOWSHEET_ID = 2

SENSOR_DEFINITIONS = [
    {
        "location": "Wall Plug",
        "measurement": "current_power",
        "unitop": "my_pump",
        "propkey": "PROP_PU_3" # Power required
    }
]

PROPERTIES = [
    {
        "unitop": "pump_outlet",
        "propkey": "PROP_MS_1",
        "propname": "Pump Outlet Pressure",
    },
    {
        "unitop": "pump_outlet",
        "propkey": "PROP_MS_2",
        "propname": "Pump Outlet Temperature",
    },
]