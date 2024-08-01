import aiohttp
import async_timeout
import logging

_LOGGER = logging.getLogger(__name__)

class StigaAPI:
    def __init__(self, email, password, session):
        self.session = session
        self.email = email
        self.password = password
        # Hard-code the API key
        self.api_key = "AIzaSyCPtRBU_hwWZYsguHp9ucGrfNac0kXR6ug"

    async def authenticate(self):
        """Authenticate with Firebase to obtain a bearer token for Stiga API."""
        url = 'https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword'
        payload = {
            'email': self.email,
            'password': self.password,
            'returnSecureToken': True
        }
        params = {'key': self.api_key}
        headers = {'Content-Type': 'application/json'}
        try:
            async with self.session.post(url, json=payload, headers=headers, params=params) as response:
                data = await response.json()
                if response.status == 200:
                    self.token = data['idToken']
                    _LOGGER.info("Successfully authenticated with Firebase")
                else:
                    _LOGGER.error(f"Authentication failed with status: {response.status} - {data}")
                    raise Exception("Authentication failed")
        except Exception as e:
            _LOGGER.error(f"Exception during authentication: {e}")
            raise

    async def get_devices(self):
        """Retrieve list of devices from Stiga."""
        if not hasattr(self, 'token'):
            _LOGGER.error("API token is not set. Authentication may have failed.")
            return []
        url = 'https://connectivity-production.stiga.com/api/garage/integration'
        headers = {'Authorization': f'Bearer {self.token}'}
        _LOGGER.debug(f"Fetching devices from {url} with token {self.token}")
        try:
            async with self.session.get(url, headers=headers) as response:
                data = await response.json()
                if response.status == 200:
                    _LOGGER.info(f"Devices fetched successfully: {data}")
                    return data
                else:
                    _LOGGER.error(f"Failed to fetch devices with status: {response.status}")
                    return []
        except Exception as e:
            _LOGGER.error(f"Error fetching devices: {e}")
            return []

    async def get_device_status(self, uuid):
        """Fetch status for a specific device."""
        url = f'https://connectivity-production.stiga.com/api/devices/{uuid}/status'
        headers = {'Authorization': f'Bearer {self.token}'}
        _LOGGER.debug(f"Fetching status for device {uuid} from {url} with token {self.token}")
        async with self.session.get(url, headers=headers) as response:
            data = await response.json()
            if response.status == 200:
                _LOGGER.info(f"Status fetched successfully for device {uuid}: {data}")
                return data
            else:
                _LOGGER.error(f"Failed to fetch status for device {uuid} with status: {response.status}")
                return {}

    async def start_mowing(self, uuid):
        """Send command to start mowing."""
        url = f'https://connectivity-production.stiga.com/api/devices/{uuid}/command/startsession'
        headers = {'Authorization': f'Bearer {self.token}'}
        await self.session.post(url, headers=headers)

    async def stop_mowing(self, uuid):
        """Send command to stop mowing."""
        url = f'https://connectivity-production.stiga.com/api/devices/{uuid}/command/endsession'
        headers = {'Authorization': f'Bearer {self.token}'}
        await self.session.post(url, headers=headers)
