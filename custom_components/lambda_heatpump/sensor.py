"""Sensor handling for Lambda Heatpump."""
from datetime import timedelta
import logging
from pymodbus.client import ModbusTcpClient
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Liste aller auslesbaren Register
SENSORS = [
    # General Ambient
    {"name": "Ambient Error Number", "register": 0, "unit": "", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
    {"name": "Ambient Operating State", "register": 1, "unit": "", "scale": 1, "precision": 0, "data_type": "uint16", "state_class": "total",
     "description_map": ["Off", "Automatik", "Manual", "Error"]},
    {"name": "Ambient Temperature", "register": 2, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Ambient Temperature 1h", "register": 3, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Ambient Temperature Calculated", "register": 4, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},

    # General E-Manager
    {"name": "E-Manager Error Number", "register": 100, "unit": "", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
    {"name": "E-Manager Operating State", "register": 101, "unit": "", "scale": 1, "precision": 0, "data_type": "uint16", "state_class": "total",
     "description_map": ["Off", "Automatik", "Manual", "Error", "Offline"]},
    {"name": "E-Manager Actual Power", "register": 102, "unit": "W", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
    {"name": "E-Manager Actual Power Consumption", "register": 103, "unit": "W", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
    {"name": "E-Manager Power Consumption Setpoint", "register": 104, "unit": "W", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},

    # Heat Pump No. 1
    {"name": "Heat Pump 1 Error State", "register": 1000, "unit": "", "scale": 1, "precision": 0, "data_type": "uint16", "state_class": "total",
     "description_map": ["OK", "Message", "Warnung", "Alarm", "Fault"]},
    {"name": "Heat Pump 1 Error Number", "register": 1001, "unit": "", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
    {"name": "Heat Pump 1 State", "register": 1002, "unit": "", "scale": 1, "precision": 0, "data_type": "uint16", "state_class": "total",
     "description_map": ["Init", "Reference", "Restart-Block", "Ready", "Start Pumps", "Start Compressor", "Pre-Regulation", "Regulation",
                         "Not Used", "Cooling", "Defrosting", "Not Used", "Not Used", "Not Used", "Not Used", "Not Used", "Not Used",
                         "Not Used", "Not Used", "Not Used", "Stopping", "Not Used", "Not Used", "Not Used", "Not Used", "Not Used",
                         "Not Used", "Not Used", "Not Used", "Not Used", "Not Used", "Fault-Lock", "Alarm-Block", "Not Used", "Not Used",
                         "Not Used", "Not Used", "Not Used", "Not Used", "Error-Reset"]},
    {"name": "Heat Pump 1 Operating State", "register": 1003, "unit": "", "scale": 1, "precision": 0, "data_type": "uint16", "state_class": "total",
     "description_map": ["Standby", "Central Heating", "Domestic Hot Water", "Cold Climate", "Circulate", "Defrost", "Off", "Frost",
                         "Standby-Frost", "Not used", "Summer", "Holiday", "Error", "Warning", "Info-Message", "Time-Block", "Release-Block",
                         "Mintemp-Block", "Firmware-Download"]},
    {"name": "Heat Pump 1 Flow Line Temperature", "register": 1004, "unit": "°C", "scale": 0.01, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heat Pump 1 Return Line Temperature", "register": 1005, "unit": "°C", "scale": 0.01, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heat Pump 1 Volume Flow Heat Sink", "register": 1006, "unit": "l/h", "scale": 1, "precision": 1, "data_type": "int16", "state_class": "total"},
    {"name": "Heat Pump 1 Energy Source Inlet Temperature", "register": 1007, "unit": "°C", "scale": 0.01, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heat Pump 1 Energy Source Outlet Temperature", "register": 1008, "unit": "°C", "scale": 0.01, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heat Pump 1 Volume Flow Energy Source", "register": 1009, "unit": "l/min", "scale": 0.01, "precision": 1, "data_type": "int16", "state_class": "measurement"},
    {"name": "Heat Pump 1 Compressor Unit Rating", "register": 1010, "unit": "%", "scale": 0.01, "precision": 0, "data_type": "uint16", "state_class": "total"},
    {"name": "Heat Pump 1 Actual Heating Capacity", "register": 1011, "unit": "kW", "scale": 0.1, "precision": 1, "data_type": "int16", "state_class": "measurement"},
    {"name": "Heat Pump 1 Inverter Power Consumption", "register": 1012, "unit": "W", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
    {"name": "Heat Pump 1 COP", "register": 1013, "unit": "", "scale": 0.01, "precision": 2, "data_type": "int16", "state_class": "total"},
    {"name": "Heat Pump 1 Request Type", "register": 1015, "unit": "", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total",
     "description_map": ["No Request", "Flow Pump Circulation", "Central Heating", "Central Cooling", "Domestic Hot Water"]},
    {"name": "Heat Pump 1 Requested Flow Line Temperature", "register": 1016, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heat Pump 1 Requested Return Line Temperature", "register": 1017, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heat Pump 1 Requested Flow to Return Line Temperature Difference", "register": 1018, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heat Pump 1 Relais State 2nd Heating Stage", "register": 1019, "unit": "", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
    {"name": "Heat Pump 1 Compressor Power Consumption Accumulated", "register": [1020, 1021], "unit": "Wh", "scale": 1, "precision": 0, "data_type": "int32", "device_class": "energy", "state_class": "total_increasing"},
    {"name": "Heat Pump 1 Compressor Thermal Energy Output Accumulated", "register": [1022, 1023], "unit": "Wh", "scale": 1, "precision": 0, "data_type": "int32", "device_class": "energy", "state_class": "total_increasing"},

    # Boiler
    {"name": "Boiler Error Number", "register": 2000, "unit": "", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
    {"name": "Boiler Operating State", "register": 2001, "unit": "", "scale": 1, "precision": 0, "data_type": "uint16", "state_class": "total",
     "description_map": ["Standby", "Domestic Hot Water", "Legio", "Summer", "Frost", "Holiday", "Prio-Stop", "Error", "Off", "Prompt-DHW",
                         "Trailing-Stop", "Temp-Lock", "Standby-Frost"]},
    {"name": "Boiler Actual High Temperature", "register": 2002, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Boiler Actual Low Temperature", "register": 2003, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Boiler Set Temperature", "register": 2050, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},

    # Buffer
    {"name": "Buffer Error Number", "register": 3000, "unit": "", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
    {"name": "Buffer Operating State", "register": 3001, "unit": "", "scale": 1, "precision": 0, "data_type": "uint16", "state_class": "total",
     "description_map": ["Standby", "Heating", "Cooling", "Summer", "Frost", "Holiday", "Prio-Stop", "Error", "Off", "Standby-Frost"]},
    {"name": "Buffer Actual High Temperature", "register": 3002, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Buffer Actual Low Temperature", "register": 3003, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Buffer Set Temperature", "register": 3050, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},

    # Solar
#    {"name": "Solar Error Number", "register": 4000, "unit": "", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
#    {"name": "Solar Operating State", "register": 4001, "unit": "", "scale": 1, "precision": 0, "data_type": "uint16", "state_class": "total",
#     "description_map": ["Standby", "Heating", "Error", "Off"]},
#    {"name": "Solar Actual Collector Temperature", "register": 4002, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
#    {"name": "Solar Actual Buffer Sensor 1 Temperature", "register": 4003, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
#    {"name": "Solar Actual Buffer Sensor 2 Temperature", "register": 4004, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
#    {"name": "Solar Set Max Buffer Temperature", "register": 4050, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
#    {"name": "Solar Set Buffer Changeover Temperature", "register": 4051, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},

    # Heating Circuit 1
    {"name": "Heating Circuit 1 Error Number", "register": 5000, "unit": "", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
    {"name": "Heating Circuit 1 Operating State", "register": 5001, "unit": "", "scale": 1, "precision": 0, "data_type": "uint16", "state_class": "total",
     "description_map": ["Heating", "Eco", "Cooling", "Floor-dry", "Frost", "Max-Temp", "Error", "Service", "Holiday", "Central Heating Summer",
                         "Central Cooling Winter", "Prio-Stop", "Off", "Release-Off", "Time-Off", "Standby", "Standby-Heating", "Standby-Eco",
                         "Standby-Cooling", "Standby-Frost", "Standby-Floor-dry"]},
    {"name": "Heating Circuit 1 Flow Line Temperature", "register": 5002, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heating Circuit 1 Return Line Temperature", "register": 5003, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heating Circuit 1 Room Device Temperature", "register": 5004, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heating Circuit 1 Set Flow Line Temperature", "register": 5005, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heating Circuit 1 Operating Mode", "register": 5006, "unit": "", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total",
     "description_map": ["Off", "Manual", "Automatik", "Auto-Heating", "Auto-Cooling", "Frost", "Summer", "Floor-dry"]},
    {"name": "Heating Circuit 1 Set Flow Line Offset Temperature", "register": 5050, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heating Circuit 1 Set Heating Mode Room Temperature", "register": 5051, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heating Circuit 1 Set Cooling Mode Room Temperature", "register": 5052, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},

    # Heating Circuit 2
    {"name": "Heating Circuit 2 Error Number", "register": 5100, "unit": "", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
    {"name": "Heating Circuit 2 Operating State", "register": 5101, "unit": "", "scale": 1, "precision": 0, "data_type": "uint16", "state_class": "total",
     "description_map": ["Heating", "Eco", "Cooling", "Floor-dry", "Frost", "Max-Temp", "Error", "Service", "Holiday", "Central Heating Summer",
                         "Central Cooling Winter", "Prio-Stop", "Off", "Release-Off", "Time-Off", "Standby", "Standby-Heating", "Standby-Eco",
                         "Standby-Cooling", "Standby-Frost", "Standby-Floor-dry"]},
    {"name": "Heating Circuit 2 Flow Line Temperature", "register": 5102, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heating Circuit 2 Return Line Temperature", "register": 5103, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heating Circuit 2 Room Device Temperature", "register": 5104, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heating Circuit 2 Set Flow Line Temperature", "register": 5105, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heating Circuit 2 Operating Mode", "register": 5106, "unit": "", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total",
     "description_map": ["Off", "Manual", "Automatik", "Auto-Heating", "Auto-Cooling", "Frost", "Summer", "Floor-dry"]},
    {"name": "Heating Circuit 2 Set Flow Line Offset Temperature", "register": 5150, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heating Circuit 2 Set Heating Mode Room Temperature", "register": 5151, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heating Circuit 2 Set Cooling Mode Room Temperature", "register": 5152, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},

    # Heating Circuit 3
    {"name": "Heating Circuit 3 Error Number", "register": 5200, "unit": "", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
    {"name": "Heating Circuit 3 Operating State", "register": 5201, "unit": "", "scale": 1, "precision": 0, "data_type": "uint16", "state_class": "total",
     "description_map": ["Heating", "Eco", "Cooling", "Floor-dry", "Frost", "Max-Temp", "Error", "Service", "Holiday", "Central Heating Summer",
                         "Central Cooling Winter", "Prio-Stop", "Off", "Release-Off", "Time-Off", "Standby", "Standby-Heating", "Standby-Eco",
                         "Standby-Cooling", "Standby-Frost", "Standby-Floor-dry"]},
    {"name": "Heating Circuit 3 Flow Line Temperature", "register": 5202, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heating Circuit 3 Return Line Temperature", "register": 5203, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heating Circuit 3 Room Device Temperature", "register": 5204, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heating Circuit 3 Set Flow Line Temperature", "register": 5205, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heating Circuit 3 Operating Mode", "register": 5206, "unit": "", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total",
     "description_map": ["Off", "Manual", "Automatik", "Auto-Heating", "Auto-Cooling", "Frost", "Summer", "Floor-dry"]},
    {"name": "Heating Circuit 3 Set Flow Line Offset Temperature", "register": 5250, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heating Circuit 3 Set Heating Mode Room Temperature", "register": 5251, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heating Circuit 3 Set Cooling Mode Room Temperature", "register": 5252, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
]

REGISTER_BLOCKS = [
    (0, 4),       # General Ambient: Register 0 bis 4
    (100, 104),   # E-Manager: Register 100 bis 104
    (1000, 1019), # Heat Pump No. 1: Register 1000 bis 1019
    (1020, 1023), # Heat Pump No. 1 (int32): Register 1020 bis 1023
    (2000, 2003), # Boiler: Register 2000 bis 2003
    (2050, 2050), # Boiler: Register 2050
    (3000, 3003), # Buffer: Register 3000 bis 3003
    (3050, 3050), # Buffer: Register 3050
    (5000, 5006), # Heating Circuit 1: Register 5000 bis 5006
    (5050, 5052), # Heating Circuit 1: Register 5050 bis 5052
    (5100, 5106), # Heating Circuit 2: Register 5100 bis 5106
    (5150, 5152), # Heating Circuit 2: Register 5150 bis 5152
    (5200, 5206), # Heating Circuit 3: Register 5200 bis 5206
    (5250, 5252), # Heating Circuit 3: Register 5250 bis 5252
]

class ModbusClientManager:
    """Manage a persistent Modbus TCP client."""

    def __init__(self, ip_address):
        self.client = ModbusTcpClient(ip_address)

    def fetch_data(self, sensors):
        """Fetch data from the Lambda Heatpump using predefined register blocks."""
        data = {}
        try:
            for start_register, end_register in REGISTER_BLOCKS:
                count = end_register - start_register + 1
                _LOGGER.debug(f"Reading registers from {start_register} to {end_register} (count: {count})")

                # Lese die Register im definierten Block
                result = self.client.read_holding_registers(start_register, count=count, slave=1)
                if result.isError():
                    _LOGGER.error(f"Error reading registers from {start_register} to {end_register}: {result}")
                    continue

                # Ordne die gelesenen Werte den Sensoren zu
                for sensor in sensors:
                    if isinstance(sensor["register"], list):  # int32
                        if start_register <= sensor["register"][0] <= end_register:
                            high = result.registers[sensor["register"][0] - start_register]
                            low = result.registers[sensor["register"][1] - start_register]
                            value = (high << 16) + low if high < 0x8000 else ((high << 16) + low - 0x100000000)
                            scaled_value = value * sensor.get("scale", 1)
                            data[sensor["name"]] = round(scaled_value, sensor.get("precision", 0))
                    elif start_register <= sensor["register"] <= end_register:  # int16/uint16
                        raw_value = result.registers[sensor["register"] - start_register]
                        if sensor.get("data_type") == "int16":
                            value = raw_value if raw_value < 0x8000 else raw_value - 0x10000
                        else:
                            value = raw_value
                        scaled_value = value * sensor.get("scale", 1)
                        data[sensor["name"]] = round(scaled_value, sensor.get("precision", 0))

        except Exception as e:
            _LOGGER.error(f"Failed to fetch data: {e}")
            data = {sensor["name"]: None for sensor in sensors}

        return data

    def close(self):
        """Close the Modbus client."""
        self.client.close()

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Lambda Heatpump sensors."""
    ip_address = entry.data["ip_address"]
    update_interval = timedelta(seconds=entry.data.get("update_interval", 30))  # Standard: 30 Sekunden

    client_manager = ModbusClientManager(ip_address)

    async def async_update_data():
        """Fetch data from the heat pump."""
        return client_manager.fetch_data(SENSORS)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Lambda Heatpump",
        update_method=async_update_data,
        update_interval=update_interval,
    )

    await coordinator.async_config_entry_first_refresh()

    # Gruppierung der Sensoren nach Kategorien
    grouped_sensors = [
        (sensor, "General Ambient") for sensor in SENSORS[:5]
    ] + [
        (sensor, "E-Manager") for sensor in SENSORS[5:10]
    ] + [
        (sensor, "Heat Pump No. 1") for sensor in SENSORS[10:31]
    ] + [
        (sensor, "Boiler") for sensor in SENSORS[31:36]
    ] + [
        (sensor, "Buffer") for sensor in SENSORS[36:41]
    ] + [
        # (sensor, "Solar") for sensor in SENSORS[41:46]  # Solar auskommentiert
    ] + [
        (sensor, "Heating Circuit 1") for sensor in SENSORS[41:51]
    ] + [
        (sensor, "Heating Circuit 2") for sensor in SENSORS[51:61]
    ] + [
        (sensor, "Heating Circuit 3") for sensor in SENSORS[61:]
    ]

    # Sensoren erstellen und hinzufügen
    sensors = [LambdaHeatpumpSensor(coordinator, sensor, device_name) for sensor, device_name in grouped_sensors]
    async_add_entities(sensors)

    # Schließe den Client beim Entladen der Integration
    hass.bus.async_listen_once("homeassistant_stop", lambda event: client_manager.close())

class LambdaHeatpumpSensor(Entity):
    """Representation of a Lambda Heatpump sensor."""

    def __init__(self, coordinator, sensor, device_name):
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._name = sensor["name"]
        self._register = sensor["register"]
        self._unit = sensor["unit"]
        self._scale = sensor.get("scale", 1)
        self._precision = sensor.get("precision", 0)
        self._data_type = sensor.get("data_type", "int16")
        self._device_class = sensor.get("device_class")
        self._state_class = sensor.get("state_class")
        self._description_map = sensor.get("description_map")
        self._device_name = device_name  # Gruppierungsname

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"lambda_heatpump_{self._register}"

    @property
    def state(self):
        """Return the state of the sensor."""
        raw_value = self._coordinator.data.get(self._name)
        if (raw_value is None) or (raw_value == 0x8000):
            return None
        # Verwenden der description_map, falls vorhanden
        if self._description_map:
            try:
                return self._description_map[int(raw_value)]
            except IndexError:
                return f"Unknown ({raw_value})"
        # Rückgabe des Werts ohne zusätzliche Skalierung
        return round(raw_value, self._precision)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        if self.unique_id in [
            "lambda_heatpump_[1020, 1021]",
            "lambda_heatpump_[1022, 1023]",
        ] or self._name in [
            "Heat Pump 1 Compressor Power Consumption Accumulated",
            "Heat Pump 1 Compressor Thermal Energy Output Accumulated",
        ]:
            _LOGGER.debug(f"Setting state_class to total_increasing for sensor {self._name} (unique_id: {self.unique_id})")
            return "total_increasing"
        _LOGGER.debug(f"Using default state_class for sensor {self._name} (unique_id: {self.unique_id})")
        return self._state_class

    @property
    def available(self):
        """Return if entity is available."""
        return self._coordinator.last_update_success

    @property
    def device_info(self):
        """Return device information for grouping sensors."""
        return {
            "identifiers": {(DOMAIN, self._device_name)},
            "name": self._device_name,
            "manufacturer": "Lambda",
            "model": "Heatpump Eureka-Luft (EU-L)",
#            "sw_version": "1.2.25",
#            "icon": icons.get(self._device_name, "mdi:gauge"),  # Standard-Icon, falls keine Übereinstimmung
        }

    async def async_update(self):
        """Update the entity."""
        await self._coordinator.async_request_refresh()
