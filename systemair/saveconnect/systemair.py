"""
python-systemair-saveconnect is a module for accessing the saveconnect HTTP/WS api to retrieve and write data.
"""
import asyncio
import json
import logging
import time
import typing

from .auth import SaveConnectAuth
from .const import UserModes, Airflow
from .data import SaveConnectData
from .graphql import SaveConnectGraphQL
from .models import SaveConnectDevice
from .register import Register
from .registry import RegisterWrite
from .websocket import WSClient

_LOGGER = logging.getLogger(__name__)


class SaveConnectTemperature:
    def __init__(self, client: "SaveConnect"):
        """
        SaveConnectTemperature
        @param client: SaveConnect object
        """
        self.sc = client

    async def set_eco_mode(self, device: SaveConnectDevice, state: bool):
        """
        Togle the eco mode according to boolean
        @param device:
        @param state: bool
        """
        await self.sc.write_data(
            device=device,
            register=RegisterWrite(register=Register.REG_USERMODE_MODE_HMI, value=state)
        )

    async def set_temperature_offset(self, device: SaveConnectDevice, temperature: int):
        """
        Set the temperature offset of a device
        @param device:
        @param temperature: the specified temperature
        """
        min_value = int(device.registry.REG_TC_SP["min"] / 10)
        max_value = int(device.registry.REG_TC_SP["max"] / 10)

        if min_value <= temperature <= max_value:
            await self.sc.write_data(
                device=device,
                register=RegisterWrite(register=Register.REG_TC_SP, value=int(temperature * 10))
            )
        else:
            raise RuntimeWarning(
                f"Could not set temperature because the value was not in bounds of {min_value} - {max_value}")


class SaveConnectUserMode:

    def __init__(self, client: "SaveConnect"):
        """
        SaveConnect UserMode interaction
        @param client: SaveConnect object
        """
        self.sc = client

    async def set_airflow(self, device, mode: Airflow):
        """
        Set the airflow value. This only works if the mode is "manual"
        @param device:
        @param mode:
        """

        return await self.sc.write_data(
            device=device,
            register=RegisterWrite(register=Register.REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF, value=mode)
        )

    async def set_mode(self, device, mode: UserModes, duration=60):
        """
        Set the operation mode of the ventilation unit.
        @param device:
        @param mode: The specified UserMode
        @param duration: optional. How many minutes/hours to run the mode
        """
        if mode in [UserModes.REFRESH, UserModes.AWAY, UserModes.CROWDED, UserModes.FIREPLACE, UserModes.HOLIDAY]:
            timer = {
                UserModes.CROWDED: Register.REG_USERMODE_CROWDED_TIME,
                UserModes.HOLIDAY: Register.REG_USERMODE_HOLIDAY_TIME,
                UserModes.FIREPLACE: Register.REG_USERMODE_FIREPLACE_TIME,
                UserModes.AWAY: Register.REG_USERMODE_AWAY_TIME,
                UserModes.REFRESH: Register.REG_USERMODE_REFRESH_TIME
            }

            await self.sc.write_data(
                device=device,
                register=RegisterWrite(register=timer[mode], value=duration)
            )

        return await self.sc.write_data(
            device=device,
            register=RegisterWrite(register=Register.REG_USERMODE_HMI_CHANGE_REQUEST, value=mode)
        )


class SaveConnect:
    """The SaveConnect that consumes the SaveConnect API."""

    def __init__(self,
                 email,
                 password,
                 ws_enabled=True,
                 url="https://sso.systemair.com/",
                 wss_url="wss://homesolutions.systemair.com/streaming/",
                 update_interval=60,
                 refresh_token_interval=300,
                 worker_interval=5,
                 loop=asyncio.get_event_loop()

                 ):
        """
        Constructor of the SaveConnect API
        @param email:
        @param password:
        @param ws_enabled: Enabling websocket will allow for PUSH_EVENTs when device is updated
        @param url: location of the SaveConnect REST API
        @param wss_url:  location of the SaveConnect WSS API
        @param update_interval: interval of how often to update via REST API
        @param refresh_token_interval: Refresh interval of the access_token
        """
        self.data = SaveConnectData()
        self.graphql = SaveConnectGraphQL(self)
        self.auth = SaveConnectAuth(loop=loop)
        self.user_mode = SaveConnectUserMode(self)
        self.temperature = SaveConnectTemperature(self)

        self._ws = WSClient(self, url=wss_url, callback=self.on_ws_data, loop=loop)

        """URL for the savecair API."""
        self.url = url

        """E-Mail for authentication to the API"""
        self.email = email

        """Password for the savecair API."""
        self.password = password  # Password to the IAM

        """If WS is enabled"""
        self.ws_enabled = ws_enabled

        """Device sensor update interval."""
        self.update_interval = update_interval

        """The tick speed of the worker loop"""
        self.worker_interval = worker_interval

        """Refresh token interval."""
        self.refresh_token_interval = refresh_token_interval

        """The asyncio loop"""
        self.loop = loop

        """Run async loop for updating sensors and refresh token."""
        loop.create_task(self.worker())

    async def worker(self):
        last_update_time = time.time()
        last_refresh_token_time = time.time()
        while True:
            now = time.time()

            if self.auth.is_auth():
                if 0 < self.update_interval < now - last_update_time:
                    _LOGGER.debug("Updating data according to update_interval.")
                    for device in await self.get_devices():
                        await self.read_data(device=device)

                    last_update_time = time.time()

                if 0 < self.refresh_token_interval < now - last_refresh_token_time:
                    _LOGGER.debug("Refreshing access tokens")
                    await self.refresh_token()

                    last_refresh_token_time = time.time()

            await asyncio.sleep(self.worker_interval)

    async def refresh_token(self):
        _LOGGER.debug("Refreshing access tokens")
        await self.auth.refresh_token()
        self._ws.set_access_token(self.auth.token)
        self.graphql.set_access_token(self.auth.token)

    async def login(self):
        """
        Authenticate using email and password to retrieve an access_token
        @return: success
        """
        success = await self.auth.auth(self.email, self.password)
        if success:
            if self.ws_enabled:
                self._ws.set_access_token(self.auth.token)
                self.loop.create_task(self._ws.connect())
            self.graphql.set_access_token(self.auth.token)
        return success

    async def on_ws_data(self, data) -> bool:
        """
        Callback for retrieving DEVICE_PUSH_EVENT's via websockets
        @param data: the raw data from the WSS API
        """
        data_json = json.loads(data)
        payload = data_json["payload"]
        device_id = payload["deviceId"]
        message_type = data_json["type"]

        if message_type == "DEVICE_CONNECTED":
            self.data.set_availability(device_id, available=True)
        elif message_type == "DEVICE_DISCONNECTED":
            self.data.set_availability(device_id, available=False)
        elif message_type == "DEVICE_PUSH_EVENT":
            if "dataItems" not in payload:
                _LOGGER.error("Could not retrieve dataItems from websocket API.")
                return False

            data_items = payload["dataItems"]
            print(data_json)
            self.data.update(device_id, data_items)

            # Finally poll for updates

            try:
                device = self.data.get_device(device_id=device_id)
                await self.read_data(device=device)
            except KeyError:
                _LOGGER.debug(f"Could not find device with ID={device_id} when polling data in WS.")
        else:
            _LOGGER.error(f"Unhandled message type for WS connection: {message_type}")
            return False

        return True

    async def read_data(self, device: SaveConnectDevice) -> bool:
        """
        Read all registers on a specific device
        @param device: SaveConnectDevice object
        @return: the data that was retrieved from the API
        """
        if not self.auth.is_auth():
            await self.refresh_token()

        status = await self.graphql.queryGetDeviceData(device.identifier)

        return status

    async def write_data(self, device: SaveConnectDevice, register: RegisterWrite, is_import=False):
        """
        Write data to a specified device
        @param device: the device
        @param register: which register to write to
        @param is_import: wether to import or not
        @return: response from API (updated state)
        """

        data = await self.graphql.queryWriteDeviceValues(
            device_id=device.identifier,
            register_pair=register,
            is_import=is_import
        )
        return data

    async def get_devices(self, update=True, fetch_device_info=True) -> typing.List[SaveConnectDevice]:
        """
        Retrieve all devices from the account query
        @return:
        """
        if not update:
            devices = list(self.data.devices.values())
        else:
            devices = await self.graphql.queryGetAccount()

        for device in devices:
            if fetch_device_info:
                await self.graphql.queryDeviceInfo(device)

        return devices

    async def update_device_info(self, devices):
        for device in devices:
            await self.graphql.queryDeviceInfo(device)

    async def test_connectivity(self):
        criteria = []

        if self.ws_enabled:
            criteria.append(self._ws.is_connected())

        return all(criteria)
