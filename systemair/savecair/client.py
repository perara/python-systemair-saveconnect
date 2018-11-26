"""
python-systemair-savecair is a module for accessing the savecair WS api to retrieve and write commands.
"""
import asyncio
import json
import logging
import os
import socket
import websockets

from systemair.savecair.cmd import Login, Read, Write

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
RETRY_TIMER = 15
USER_MODES = {
    0: 'auto',
    1: 'manual',
    2: 'crowded',
    3: 'refresh',
    4: 'fireplace',
    5: 'idle',
    6: 'holiday'
}


class SavecairClient:
    """The SacecairClient that consumes the savecair API."""

    def __init__(self, iam_id, password, loop=asyncio, url="wss://savecair.systemair.com/ws/", params=None, retry=True):
        """Constructor of the python-savecair-client."""

        """Loop determines which async module to use."""
        self.loop = loop

        """URL for the savecair API."""
        self.url = url

        """IAM for the savcecair API."""
        self.iam = iam_id

        """Password for the savecair API."""
        self.password = password  # Password to the IAM

        """Retry parameter for reconnecting to the WS api."""
        self.retry = retry

        """Coroutines for when client connects."""
        self.on_connect = [self._on_connect]

        """Coroutines for when the client disconnects."""
        self.on_disconnect = [self._on_disconnect]

        """Coroutines for when the client retrieves an update."""
        self.on_update = [self._on_update]  #

        """Coroutines for when the client exits abnormaly."""
        self.on_error = []

        """Stores the WS connection object."""
        self.connection = None

        """Keeps track of the state of the savecair device."""
        self.data = {}

        """Load parameters from file or arguments."""
        self.params = params if isinstance(params, list) else list(self._load_parameters())

    def start(self):
        self.loop.create_task(self._connect())

    async def _on_connect(self):
        """Callback for when the socket is connected."""
        _LOGGER.debug("Requesting update from sensors")
        await self.send(Read(self.params))

    async def _on_disconnect(self):
        """Callback for when the socket is disconnected."""
        _LOGGER.debug("Disconnected from server")
        if self.retry:
            await asyncio.sleep(RETRY_TIMER)
            await self._connect()

    async def _on_update(self):
        """Callback for when a package is a received."""
        _LOGGER.debug("Received data update")

    async def _connect(self):
        """Start websocket connection."""
        try:
            async with websockets.connect(self.url) as _wb:
                self.connection = _wb

                """Send login string."""
                await self.send(Login(self.iam, self.password))

                """Run data handler."""
                await self._handler()

            self.connection = None
            await self._connect()
        except socket.gaierror as _e:
            self.connection = None
            _ = [await _() for _ in self.on_disconnect]  # Call on_update callbacks

    def _load_parameters(self):
        """Function for loading the parameter list."""
        for param in open(os.path.join(DIR_PATH, "parameters.txt")).read().splitlines():
            param = param.split("#")[0]  # Remove comments
            param = param.strip()  # Remove whitespaces
            if not param:
                # Remove empty lines
                continue
            yield param

    async def _handler(self):
        """"Websocket handler which receives messages."""
        while True:
            try:
                msg = await self.connection.recv()  # Receive raw data

                try:
                    data = json.loads(msg)
                except ValueError as error:
                    _LOGGER.error("Message from server is not JSON: %s", error)
                    continue


                if data["type"] == "LOGGED_IN":
                    _LOGGER.debug("Client connected to server.")
                    _ = [await _() for _ in self.on_connect]  # Call on_update callbacks

                elif data["type"] == "READ" or data["type"] == "VALUE_CHANGED":

                    if "readValues" in data:
                        _LOGGER.debug("readValues: %s", data)
                        values = data["readValues"]
                    elif "changedValues" in data:
                        _LOGGER.debug("changedValues: %s", data)
                        values = data["changedValues"]
                    else:
                        _LOGGER.warning("The read commend is not implemented correctly: %s", data)
                        continue

                    self.data.update(values)
                    _ = [await _() for _ in self.on_update]  # Call on_update callbacks
                elif data["type"] == "ERROR":
                    _LOGGER.error(data)

            except websockets.exceptions.ConnectionClosed:
                _LOGGER.error('Connection to WS server was closed!')
                _ = [await _() for _ in self.on_disconnect]  # Call on_update callbacks
                break

    async def send(self, data):
        """Send a message through the websocket channel."""
        if self.connection is None or not self.connection.open:
            _LOGGER.warning("Tried to send query when connection does not exists!")
            return False
        print(str(data))
        await self.connection.send(str(data))

    def get(self, key):
        """Retrieve data from the dictionary."""
        if key not in self.data:
            return None

        return self.data[key]

    async def set_temperature(self, value):
        """Set the temperature of the ventilation unit."""
        await self.send(Write(dict(main_temperature_offset=int(value * 10))))

    async def set_manual_mode(self):
        """Set the ventilation unit in manual mode."""
        await self.send(Write(dict(
            mode_change_request="1"
        )))

    async def set_crowded_mode(self):
        """Set the ventilation unit in crowded mode."""
        await self.send(Write(dict(
            user_mode_crowded_duration=8,
            mode_change_request="2"
        )))

    async def set_refresh_mode(self):
        """Set the ventilation unit in refresh mode."""
        await self.send(Write(dict(
            user_mode_refresh_duration=240,
            mode_change_request="3"
        )))

    async def set_fireplace_mode(self):
        """Set the ventilation unit in fireplace mode."""
        await self.send(Write(dict(
            user_mode_fireplace_duration=60,
            mode_change_request="4"
        )))

    async def set_holiday_mode(self):
        """Set the ventilation unit in holiday mode."""
        await self.send(Write(dict(
            user_mode_holiday_duration=365,
            mode_change_request="6"
        )))

    async def set_auto_mode(self):
        """Set the ventilation unit in auto mode."""
        await self.send(Write(dict(mode_change_request="0")))

    async def set_away_mode(self):
        """Set the ventilation unit in away mode."""
        await self.send(Write(dict(
            user_mode_away_duration=72,
            mode_change_request="5"
        )))

    async def set_fan_off(self):
        """Set the fan speed to off."""
        await self.send(Write(dict(main_airflow="1")))

    async def set_fan_low(self):
        """Set the fan speed to low."""
        await self.send(Write(dict(main_airflow="2")))

    async def set_fan_normal(self):
        """Set the fan speed to normal."""
        await self.send(Write(dict(main_airflow="3")))

    async def set_fan_high(self):
        """Set the fan speed to high."""
        await self.send(Write(dict(main_airflow="4")))

    async def update_sensors(self):
        """Update available sensors via the API."""
        await self.send(Read(self.params))

    async def set_operation_mode(self, operation_mode):
        if operation_mode.lower() == "auto":
            await self.set_auto_mode()
        elif operation_mode.lower() == "manual":
            await self.set_manual_mode()
        elif operation_mode.lower() == "crowded":
            await self.set_crowded_mode()
        elif operation_mode.lower() == "refresh":
            await self.set_refresh_mode()
        elif operation_mode.lower() == "fireplace":
            await self.set_fireplace_mode()
        elif operation_mode.lower() == "holiday":
            await self.set_holiday_mode()

    async def set_fan_mode(self, fan_mode):
        if fan_mode == "Off":
            await self.set_fan_off()
        elif fan_mode == "Low":
            await self.set_fan_low()
        elif fan_mode == "Medium":
            await self.set_fan_normal()
        elif fan_mode == "High":
            await self.set_fan_high()

    def get_current_operation(self):
        if "main_user_mode" not in self.data:
            return None

        if self.data["main_user_mode"] is None:
            return None

        opcode = int(self.data["main_user_mode"])

        try:
            return USER_MODES[opcode]
        except KeyError:
            return None
