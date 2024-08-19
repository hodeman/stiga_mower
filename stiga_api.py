import aiohttp
import async_timeout
import logging
import json  # Add this import for JSON parsing

_LOGGER = logging.getLogger(__name__)

class StigaAPI:
    def __init__(self, email, password, session):
        self.session = session
        self.email = email
        self.password = password
        self.api_key = "AIzaSyCPtRBU_hwWZYsguHp9ucGrfNac0kXR6ug"
        self.token = None

    async def authenticate(self):
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
        if not self.token:
            await self.authenticate()
        url = 'https://connectivity-production.stiga.com/api/garage/integration'
        headers = {'Authorization': f'Bearer {self.token}'}
        _LOGGER.debug(f"Fetching devices from {url} with token {self.token}")
        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                _LOGGER.info(f"Devices fetched successfully: {data}")
                return data
            elif response.status == 401:
                _LOGGER.warning("Token expired or unauthorized, re-authenticating...")
                await self.authenticate()
                return await self.get_devices()
            else:
                _LOGGER.error(f"Failed to fetch devices with status: {response.status}")
                return []

    async def get_device_status(self, uuid):
        url = f'https://connectivity-production.stiga.com/api/devices/{uuid}/mqttstatus'
        headers = {'Authorization': f'Bearer {self.token}'}
        _LOGGER.debug(f"Fetching status for device {uuid} from {url} with token {self.token}")
        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                
                # Extract relevant information
                device_info = data['data']['attributes']['device_info']
                status_description = json.loads(device_info['status']['description'])
                battery_description = json.loads(device_info['battery']['description'])
                
                return {
                    "mowing_mode": status_description.get("mowingMode"),
                    "current_action": status_description.get("currentAction"),
                    "battery_percentage": battery_description.get("percentage")
                }
            elif response.status == 401:
                _LOGGER.warning("Token expired or unauthorized, re-authenticating...")
                await self.authenticate()
                return await self.get_device_status(uuid)
            else:
                _LOGGER.error(f"Failed to fetch status for device {uuid} with status: {response.status}")
                return None

    async def start_mowing(self, uuid):
        url = f'https://connectivity-production.stiga.com/api/devices/{uuid}/command/startsession'
        headers = {'Authorization': f'Bearer {self.token}'}
        await self.session.post(url, headers=headers)

    async def stop_mowing(self, uuid):
        url = f'https://connectivity-production.stiga.com/api/devices/{uuid}/command/endsession'
        headers = {'Authorization': f'Bearer {self.token}'}
        await self.session.post(url, headers=headers)
