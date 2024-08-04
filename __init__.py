import logging
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN
from .stiga_api import StigaAPI

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up STIGA Mower from a config entry."""
    session = async_get_clientsession(hass)
    api = StigaAPI(entry.data['email'], entry.data['password'], session)
    await api.authenticate()

    async def async_update_data():
        """Fetch data from API endpoint."""
        try:
            return await api.get_devices()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="stiga_mower",
        update_method=async_update_data,
        update_interval=timedelta(minutes=1),
    )

    await coordinator.async_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

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

    await hass.config_entries.async_forward_entry_setups(entry, ['sensor'])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms(entry, ['sensor'])

    if entry.entry_id in hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, 'start_mowing')
        hass.services.async_remove(DOMAIN, 'stop_mowing')
        hass.data[DOMAIN].pop(entry.entry_id)

    return True
