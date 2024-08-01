import logging
from homeassistant.helpers.entity import Entity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Stiga Mower sensor platform."""
    api = hass.data[DOMAIN][entry.entry_id]['api']
    devices_response = await api.get_devices()

    if devices_response and 'data' in devices_response:
        devices = devices_response['data']
        _LOGGER.debug(f"Device data: {devices}")

        entities = []
        for device in devices:
            device_info = device['attributes']
            entity = StigaMowerEntity(device_info, api)
            entities.append(entity)
        async_add_entities(entities)
    else:
        _LOGGER.error("No devices found or unable to fetch devices.")

class StigaMowerEntity(Entity):
    def __init__(self, device_info, api):
        self._device_info = device_info
        self.api = api
        self._state = None
        self._attributes = {
            'uuid': device_info['uuid'],
            'product_code': device_info['product_code'],
            'serial_number': device_info['serial_number'],
            'device_type': device_info['device_type'],
        }

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
    def extra_state_attributes(self):
        return self._attributes

    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            status = await self.api.get_device_status(self._device_info['uuid'])
            if status:
                self._state = status.get('state', 'unknown')
                self._attributes.update(status)
            else:
                self._state = 'unknown'
        except Exception as e:
            _LOGGER.error(f"Error updating sensor {self._device_info.get('name')}: {e}")
            self._state = 'unknown'
