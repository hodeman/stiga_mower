import logging
from homeassistant.helpers.entity import Entity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up STIGA Mower sensor based on a config entry."""
    api = hass.data[DOMAIN][entry.entry_id]
    devices_response = await api.get_devices()
    devices = devices_response.get('data', [])
    if not devices:
        _LOGGER.error("No devices found or unable to fetch devices.")
        return

    _LOGGER.debug(f"Device data: {devices}")
    sensors = [StigaMowerEntity(device['attributes'], api) for device in devices]
    async_add_entities(sensors, True)

class StigaMowerEntity(Entity):
    def __init__(self, device_info, api):
        self._device_info = device_info
        self._state = None
        self.api = api

    @property
    def name(self):
        return self._device_info.get('name')

    @property
    def unique_id(self):
        return self._device_info.get('uuid')

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        return {
            'uuid': self._device_info.get('uuid'),
            'product_code': self._device_info.get('product_code'),
            'serial_number': self._device_info.get('serial_number'),
            'device_type': self._device_info.get('device_type')
        }

    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            status = await self.api.get_device_status(self._device_info['uuid'])
            self._state = status.get('state', 'unknown')
        except Exception as e:
            _LOGGER.error(f"Error updating sensor {self._device_info.get('name')}: {e}")
