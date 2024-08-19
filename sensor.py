import logging
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    api = data["api"]

    # Setup the DataUpdateCoordinator to refresh data periodically
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="stiga_mower",
        update_method=api.get_devices,
        update_interval=timedelta(minutes=5),  # Adjust this as needed
    )
    await coordinator.async_config_entry_first_refresh()

    devices_response = coordinator.data
    _LOGGER.debug(f"Devices fetched: {devices_response}")

    entities = []
    if isinstance(devices_response, dict) and 'data' in devices_response:
        devices = devices_response['data']
        for device in devices:
            attributes = device.get('attributes', {})
            if attributes:
                uuid = attributes.get('uuid')
                serial_number = attributes.get('serial_number')
                name = attributes.get('name')
                entities.append(StigaMowerSensor(coordinator, uuid, serial_number, name, api))
            else:
                _LOGGER.error(f"Unexpected device attributes format: {device}")
    else:
        _LOGGER.error(f"Unexpected devices format: {devices_response}")

    async_add_entities(entities, True)

class StigaMowerSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, uuid, serial_number, name, api):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.api = api
        self.uuid = uuid
        self.serial_number = serial_number
        self._attr_name = name  # Use only the actual name of the device
        self._attr_unique_id = uuid
        self._state = None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            'serial_number': self.serial_number,
            'uuid': self.uuid
        }

    async def async_update(self):
        """Fetch new state data for the sensor."""
        status = await self.api.get_device_status(self.uuid)
        if status:
            self._state = status.get('state')
