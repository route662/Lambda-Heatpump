from homeassistant.helpers.entity import Entity
from .lambda_heatpump_api import get_lambda_data

SENSORS = [
    {"name": "Heatpump Temperature", "register": 3000, "unit": "°C"},
    {"name": "Hot Water Temperature", "register": 3001, "unit": "°C"},
    {"name": "Outdoor Temperature", "register": 3002, "unit": "°C"},
    {"name": "Flow Temperature", "register": 3003, "unit": "°C"},
    {"name": "Return Temperature", "register": 3004, "unit": "°C"},
    {"name": "Power Consumption", "register": 3005, "unit": "W"},
    {"name": "Compressor Speed", "register": 3006, "unit": "%"},
    {"name": "Pump Speed", "register": 3007, "unit": "%"},
    {"name": "Energy Produced", "register": 3008, "unit": "kWh"},
    {"name": "Operating Mode", "register": 3010, "unit": ""},
    {"name": "Error Code", "register": 3011, "unit": ""},
]

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    ip_address = discovery_info["ip_address"]
    sensors = [LambdaHeatpumpSensor(ip_address, sensor) for sensor in SENSORS]
    async_add_entities(sensors, update_before_add=True)

class LambdaHeatpumpSensor(Entity):
    def __init__(self, ip_address, sensor_info):
        self._ip_address = ip_address
        self._name = sensor_info["name"]
        self._register = sensor_info["register"]
        self._unit = sensor_info["unit"]
        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self._unit

    def update(self):
        self._state = get_lambda_data(self._ip_address, self._register)
