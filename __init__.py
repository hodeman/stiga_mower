import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import discovery
from .const import DOMAIN
from .stiga_api import StigaAPI

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up STIGA Mower from a config entry."""
    session = async_get_clientsession(hass)
    api = StigaAPI(entry.data['email'], entry.data['password'], session)

    try:
        await api.authenticate()
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = api

        await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

        # Initialize input_select with mower names
        await update_input_select(hass, api, entry)
        return True
    except Exception as e:
        _LOGGER.error(f"Failed to authenticate or setup Stiga API: {str(e)}")
        return False

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    try:
        await hass.config_entries.async_forward_entry_unload(entry, "sensor")
        hass.data[DOMAIN].pop(entry.entry_id)
        return True
    except ValueError:
        return False

async def update_input_select(hass, api, entry):
    try:
        devices_response = await api.get_devices()
        devices = devices_response.get('data', [])
        if devices:
            options = [device['attributes']['name'] for device in devices]
            mower_map = {device['attributes']['name']: device['attributes']['uuid'] for device in devices}
            hass.states.async_set(
                "input_select.stiga_mower",
                options[0] if options else "No Mowers Found",
                attributes={"options": options, "mower_map": mower_map}
            )
            hass.data[DOMAIN][entry.entry_id]['mower_map'] = mower_map
        else:
            _LOGGER.error("No devices found. Unable to populate input select.")
    except Exception as e:
        _LOGGER.error(f"Failed to fetch devices: {e}")
