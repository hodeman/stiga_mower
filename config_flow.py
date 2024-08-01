import voluptuous as vol
import logging
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .stiga_api import StigaAPI

LOGGER = logging.getLogger(__name__)

@callback
def configured_instances(hass):
    """Return a set of configured STIGA instances."""
    return set(entry.title for entry in hass.config_entries.async_entries(DOMAIN))

class StigaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for STIGA Mower."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Validate and save user input
            email = user_input['email']
            password = user_input['password']
            
            # Attempt to authenticate
            session = async_get_clientsession(self.hass)
            api = StigaAPI(email, password, session)
            try:
                await api.authenticate()
                LOGGER.debug("Authentication successful")
                return self.async_create_entry(title="STIGA Mower", data=user_input)
            except Exception as e:
                LOGGER.error(f"Authentication error: {e}")
                errors['base'] = 'auth'

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("email"): str,
                vol.Required("password"): str
            }),
            errors=errors,
        )
