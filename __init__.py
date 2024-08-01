import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN
from .stiga_api import StigaAPI

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up STIGA Mower from a config entry."""
    session = async_get_clientsession(hass)
    api = StigaAPI(entry.data['email'], entry.data['password'], session)
    await api.authenticate()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = api

    async def handle_start_mowing(call):
        """Handle the service call to start mowing."""
        uuid = call.data.get('uuid')
        await api.start_mowing(uuid)
        _LOGGER.info(f"Started mowing session for mower with UUID: {uuid}")

    async def handle_stop_mowing(call):
        """Handle the service call to stop mowing."""
        uuid = call.data.get('uuid')
        await api.stop_mowing(uuid)
        _LOGGER.info(f"Stopped mowing session for mower with UUID: {uuid}")

    hass.services.async_register(DOMAIN, 'start_mowing', handle_start_mowing)
    hass.services.async_register(DOMAIN, 'stop_mowing', handle_stop_mowing)

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, 'sensor')
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    if DOMAIN in hass.data:
        hass.services.async_remove(DOMAIN, 'start_mowing')
        hass.services.async_remove(DOMAIN, 'stop_mowing')
        hass.data.pop(DOMAIN)

    return True
