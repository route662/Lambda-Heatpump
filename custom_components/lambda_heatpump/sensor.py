"""Sensor handling for Lambda Heatpump."""
from datetime import timedelta
import logging
from pymodbus.client.sync import ModbusTcpClient
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

# Liste aller auslesbaren Register
SENSORS = [
    # General Ambient
    {"name": "Ambient Error Number", "register": 0, "unit": "", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
    {"name": "Ambient Operating State", "register": 1, "unit": "", "scale": 1, "precision": 0, "data_type": "uint16", "state_class": "total"},
    {"name": "Ambient Temperature", "register": 2, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Ambient Temperature 1h", "register": 3, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Ambient Temperature Calculated", "register": 4, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},

    # General E-Manager
    {"name": "E-Manager Error Number", "register": 100, "unit": "", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
    {"name": "E-Manager Operating State", "register": 101, "unit": "", "scale": 1, "precision": 0, "data_type": "uint16", "state_class": "total"},
    {"name": "E-Manager Actual Power", "register": 102, "unit": "W", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
    {"name": "E-Manager Actual Power Consumption", "register": 103, "unit": "W", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
    {"name": "E-Manager Power Consumption Setpoint", "register": 104, "unit": "W", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},

    # Heat Pump No. 1
    {"name": "Heat Pump 1 Error State", "register": 1000, "unit": "", "scale": 1, "precision": 0, "data_type": "uint16", "state_class": "total"},
    {"name": "Heat Pump 1 Error Number", "register": 1001, "unit": "", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
    {"name": "Heat Pump 1 State", "register": 1002, "unit": "", "scale": 1, "precision": 0, "data_type": "uint16", "state_class": "total"},
    {"name": "Heat Pump 1 Operating State", "register": 1003, "unit": "", "scale": 1, "precision": 0, "data_type": "uint16", "state_class": "total"},
    {"name": "Heat Pump 1 Flow Line Temperature", "register": 1004, "unit": "°C", "scale": 0.01, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heat Pump 1 Return Line Temperature", "register": 1005, "unit": "°C", "scale": 0.01, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heat Pump 1 Volume Flow Heat Sink", "register": 1006, "unit": "l/h", "scale": 1, "precision": 1, "data_type": "int16", "state_class": "total"},
    {"name": "Heat Pump 1 Energy Source Inlet Temperature", "register": 1007, "unit": "°C", "scale": 0.01, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heat Pump 1 Energy Source Outlet Temperature", "register": 1008, "unit": "°C", "scale": 0.01, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heat Pump 1 Volume Flow Energy Source", "register": 1009, "unit": "l/min", "scale": 0.01, "precision": 1, "data_type": "int16", "state_class": "total"},
    {"name": "Heat Pump 1 Compressor Unit Rating", "register": 1010, "unit": "%", "scale": 0.01, "precision": 0, "data_type": "uint16", "state_class": "total"},
    {"name": "Heat Pump 1 Actual Heating Capacity", "register": 1011, "unit": "kW", "scale": 0.1, "precision": 1, "data_type": "int16", "state_class": "total"},
    {"name": "Heat Pump 1 Inverter Power Consumption", "register": 1012, "unit": "W", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
    {"name": "Heat Pump 1 COP", "register": 1013, "unit": "", "scale": 0.01, "precision": 2, "data_type": "int16", "state_class": "total"},
    {"name": "Heat Pump 1 Request Type", "register": 1015, "unit": "", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
    {"name": "Heat Pump 1 Requested Flow Line Temperature", "register": 1016, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heat Pump 1 Requested Return Line Temperature", "register": 1017, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heat Pump 1 Requested Flow to Return Line Temperature Difference", "register": 1018, "unit": "°C", "scale": 0.1, "precision": 1, "data_type": "int16", "device_class": "temperature", "state_class": "measurement"},
    {"name": "Heat Pump 1 Relais State 2nd Heating Stage", "register": 1019, "unit": "", "scale": 1, "precision": 0, "data_type": "int16", "state_class": "total"},
    {"name": "Heat Pump 1 Compressor Power Consumption Accumulated", "register": 1020, "unit": "Wh", "scale": 1, "precision": 0, "data_type": "int32", "state_class": "total"},
    {"name": "Heat Pump 1 Compressor Thermal Energy Output Accumulated", "register": 1022, "unit": "Wh", "scale": 1, "precision": 0, "data_type": "int32", "state_class": "total"},
]

class ModbusClientManager:
    """Manage a persistent Modbus TCP client."""
    def __init__(self, ip_address):
        self.client = ModbusTcpClient(ip_address)

    def fetch_data(self, sensors):
        """Fetch data from the Lambda Heatpump."""
        data = {}
        for sensor in sensors:
            result = self.client.read_holding_registers(sensor["register"], 1, unit=1)
            if result.isError():
                _LOGGER.error(f"Error reading register {sensor['register']}")
                data[sensor["name"]] = None
            else:
                data[sensor["name"]] = result.registers[0]
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

    sensors = [LambdaHeatpumpSensor(coordinator, sensor) for sensor in SENSORS]
    async_add_entities(sensors)

    # Schließe den Client beim Entladen der Integration
    hass.bus.async_listen_once("homeassistant_stop", lambda event: client_manager.close())

class LambdaHeatpumpSensor(Entity):
    """Representation of a Lambda Heatpump sensor."""

    def __init__(self, coordinator, sensor):
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
        if raw_value is None:
            return None
        # Anwenden von Skalierung und Präzision
        scaled_value = raw_value * self._scale
        return round(scaled_value, self._precision)

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
        return self._state_class

    @property
    def available(self):
        """Return if entity is available."""
        return self._coordinator.last_update_success

    async def async_update(self):
        """Update the entity."""
        await self._coordinator.async_request_refresh()
