"""Sensor handling for Lambda Heatpump."""
from datetime import timedelta
import logging
from pymodbus.client.sync import ModbusTcpClient
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

# Liste aller auslesbaren Register
SENSORS = [
    {"name": "Vorlauftemperatur", "register": 3000, "unit": "°C"},
    {"name": "Rücklauftemperatur", "register": 3001, "unit": "°C"},
    {"name": "Warmwassertemperatur", "register": 3002, "unit": "°C"},
    {"name": "Außentemperatur", "register": 3003, "unit": "°C"},
    {"name": "Betriebsmodus", "register": 3004, "unit": ""},
    {"name": "Fehlercode", "register": 3005, "unit": ""},
    {"name": "Leistungsaufnahme", "register": 3006, "unit": "W"},
    {"name": "Gesamtenergieverbrauch", "register": 3007, "unit": "kWh"},
    {"name": "Kompressordrehzahl", "register": 3008, "unit": "%"},
    {"name": "Pumpendrehzahl", "register": 3009, "unit": "%"},
    {"name": "Systemdruck", "register": 3010, "unit": "bar"},
    {"name": "Laufzeit des Kompressors", "register": 3011, "unit": "h"},
    {"name": "Laufzeit der Pumpe", "register": 3012, "unit": "h"},
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

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._coordinator.data.get(self._name)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def available(self):
        """Return if entity is available."""
        return self._coordinator.last_update_success

    async def async_update(self):
        """Update the entity."""
        await self._coordinator.async_request_refresh()
