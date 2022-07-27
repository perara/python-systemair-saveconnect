"""
python-systemair-saveconnect is a module for accessing the saveconnect HTTP/WS api to retrieve and write data.
"""
import asyncio
import json
import logging
import time

from .auth import SaveConnectAuth
from .const import UserModes, Register, Airflow
from .data import SaveConnectData
from .graphql import SaveConnectGraphQL
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

    async def set_eco_mode(self, device_id, state: bool):
        """
        Togle the eco mode according to boolean
        @param device_id:
        @param state: bool
        """
        await self.sc.write_data(
            device_id=device_id,
            register=RegisterWrite(register=Register.TEMPERATURE_ECO_MODE_WRITE, value=state)
        )

    async def set_temperature_offset(self, device_id, temperature: int):
        """
        Set the temperature offset of a device
        @param device_id:
        @param temperature: the specified temperature
        """
        min_value = int(self.sc.data.get(device_id, Register.TEMPERATURE_OFFSET, "min") / 10)
        max_value = int(self.sc.data.get(device_id, Register.TEMPERATURE_OFFSET, "max") / 10)

        if min_value <= temperature <= max_value:
            await self.sc.write_data(
                device_id=device_id,
                register=RegisterWrite(register=Register.TEMPERATURE_OFFSET, value=int(temperature * 10))
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

    async def set_airflow(self, device_id, mode: Airflow):
        """
        Set the airflow value. This only works if the mode is "manual"
        @param device_id:
        @param mode:
        """

        await self.sc.write_data(
            device_id=device_id,
            register=RegisterWrite(register=Register.AIRFLOW_WRITE, value=mode)
        )

    async def set_mode(self, device_id, mode: UserModes, duration=60):
        """
        Set the operation mode of the ventilation unit.
        @param device_id:
        @param mode: The specified UserMode
        @param duration: optional. How many minutes/hours to run the mode
        """
        if mode in [UserModes.REFRESH, UserModes.AWAY, UserModes.CROWDED, UserModes.FIREPLACE, UserModes.HOLIDAY]:
            timer = {
                UserModes.CROWDED: Register.USER_MODE_CROWDED_TIME,
                UserModes.HOLIDAY: Register.USER_MODE_HOLIDAY_TIME,
                UserModes.FIREPLACE: Register.USER_MODE_FIREPLACE_TIME,
                UserModes.AWAY: Register.USER_MODE_AWAY_TIME,
                UserModes.REFRESH: Register.USER_MODE_REFRESH_TIME
            }

            await self.sc.write_data(
                device_id=device_id,
                register=RegisterWrite(register=timer[mode], value=duration)
            )

        await self.sc.write_data(
            device_id=device_id,
            register=RegisterWrite(register=Register.USER_MODE_WRITE, value=mode)
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
        self.graphql = SaveConnectGraphQL(data=self.data)
        self.auth = SaveConnectAuth()
        self.user_mode = SaveConnectUserMode(self)
        self.temperature = SaveConnectTemperature(self)

        self._ws = WSClient(url=wss_url, callback=self.on_ws_data, loop=loop)

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
                if self.update_interval and now - last_update_time > self.update_interval:
                    _LOGGER.debug("Updating data according to update_interval.")
                    for device in await self.get_devices():
                        await self.read_data(device_id=device["identifier"])

                    last_update_time = time.time()

                if self.refresh_token_interval and now - last_refresh_token_time > self.refresh_token_interval:
                    _LOGGER.debug("Refreshing access tokens")
                    await self.auth.refresh_token()
                    self._ws.set_access_token(self.auth.token)
                    self.graphql.set_access_token(self.auth.token)

                    last_refresh_token_time = time.time()

            await asyncio.sleep(self.worker_interval)


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

    async def on_ws_data(self, data):
        """
        Callback for retrieving DEVICE_PUSH_EVENT's via websockets
        @param data: the raw data from the WSS API
        """
        data_json = json.loads(data)
        payload = data_json["payload"]
        device_id = payload["deviceId"]
        data_items = payload["dataItems"]
        self.data.update(device_id, data_items)

    async def read_data(self, device_id):
        """
        Read all registers on a specific device
        @param device_id: device ID
        @return: the data that was retrieved from the API
        """
        data = await self.graphql.queryGetDeviceData(device_id)
        data = data["GetDeviceView"]["dataItems"]
        return data

    async def write_data(self, device_id, register: RegisterWrite, is_import=False):
        """
        Write data to a specified device
        @param device_id: the device ID
        @param register: which register to write to
        @param is_import: wether to import or not
        @return: response from API (updated state)
        """
        return await self.graphql.queryWriteDeviceValues(
            device_id=device_id,
            register_pair=register,
            is_import=is_import
        )

    async def get_devices(self):
        """
        Retrieve all devices from the account query
        @return:
        """
        data = await self.graphql.queryGetAccount()
        return data["GetAccount"]["devices"]


