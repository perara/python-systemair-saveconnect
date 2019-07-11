"""
python-systemair-savecair is a module for accessing the savecair WS api to retrieve and write commands.
"""
import asyncio
import json
import logging
import os

from .const import SA_FAN_MODE_OFF, SA_FAN_MODE_LOW, SA_FAN_MODE_MEDIUM, \
    SA_FAN_MODE_HIGH, SA_OPERATION_MODE_HOLIDAY, SA_OPERATION_MODE_FIREPLACE, SA_OPERATION_MODE_REFRESH, \
    SA_OPERATION_MODE_CROWDED, SA_OPERATION_MODE_MANUAL, SA_OPERATION_MODE_AUTO, SENSOR_CURRENT_OPERATION, \
    USER_MODE, POSTPROCESS_MAP, SENSOR_TARGET_TEMPERATURE, SENSOR_MODE_CHANGE_REQUEST, SA_OPERATION_MODE_IDLE, \
    SENSOR_CURRENT_FAN_MODE, SENSOR_CUSTOM_OPERATION, SA_OPERATION_MODE_OFF, SA_FAN_MODE_MAXIMUM

from . import const
import websockets
from .command import write, read, login

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
RETRY_TIMER = 15


class SystemAIR:
    """The SacecairClient that consumes the savecair API."""

    def __init__(self,
                 iam_id,
                 password,
                 loop=asyncio,
                 url="wss://homesolutions.systemair.com/ws/",
                 retry=True,
                 update_interval=10
                 ):
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

        """Coroutines for when the client has retrieved all updates"""
        self.on_update_done = []  #

        """Coroutines for when the client exits abnormaly."""
        self.on_error = []

        """Stores the WS connection object."""
        self.connection = None

        """Keeps track of the state of the savecair device."""
        self.data = {}

        """Load parameters from file or arguments."""
        self.available_sensors = set(SystemAIR._load_sensors())
        self.subscribed_sensors = set()

        """Flag that is set when a graceful shutdown/disconnect is initiated"""
        self.is_graceful_disconnect = False

        """Sensor update interval."""
        self.update_interval = update_interval

        """List of all running tasks"""
        self.tasks = []

    async def connect(self):
        self.loop.create_task(self._connect())

    async def _on_connect(self):
        """Callback for when the socket is connected."""
        _LOGGER.debug("Requesting update from sensors")

        task = self.loop.create_task(self.periodic_task(
            self.update_sensors,
            self.update_interval
        ))
        self.tasks.append(task)

    async def periodic_task(self, task, delay):
        while True:
            await task()
            await asyncio.sleep(delay)

    async def shutdown(self):
        self.is_graceful_disconnect = True
        self.retry = False
        await self._on_disconnect()

    async def disconnect(self):
        await self.fire_events(self.on_disconnect)

    async def _on_disconnect(self):
        """Callback for when the socket is disconnected."""
        if self.connection is not None:
            await self.connection.close()
        self.connection = None

        """Cancel running tasks and clear the task list."""
        for task in self.tasks:
            task.cancel()
        self.tasks.clear()

        _LOGGER.info("Disconnected from server")

        if self.retry:
            await asyncio.sleep(RETRY_TIMER)
            await self.connect()

    async def _on_update(self, key, value):
        """Callback for when a package is a received."""
        _LOGGER.debug("Received data update: %s => %s" % (key, value))

        if key == SENSOR_CURRENT_OPERATION:
            custom_operation = None
            custom_fan_mode = self.data.get(SENSOR_CURRENT_FAN_MODE)

            if value in [
                SA_OPERATION_MODE_CROWDED,
                SA_OPERATION_MODE_FIREPLACE,
                SA_OPERATION_MODE_REFRESH,
                SA_OPERATION_MODE_HOLIDAY,
                SA_OPERATION_MODE_IDLE,
                SA_OPERATION_MODE_AUTO,
            ]:
                if value in [SA_OPERATION_MODE_REFRESH, SA_OPERATION_MODE_FIREPLACE, SA_OPERATION_MODE_CROWDED]:
                    custom_fan_mode = SA_FAN_MODE_MAXIMUM
                elif value in [SA_OPERATION_MODE_HOLIDAY, SA_OPERATION_MODE_IDLE]:
                    custom_fan_mode = SA_FAN_MODE_LOW
                elif value in [SA_OPERATION_MODE_AUTO]:
                    custom_fan_mode = SA_FAN_MODE_HIGH

                custom_operation = "auto"
            elif value in [SA_OPERATION_MODE_MANUAL]:
                custom_operation = "auto"

            await self.fire_on_update({
                "custom_operation": custom_operation,
                'custom_fan_mode': custom_fan_mode
            })

        elif key == SENSOR_CURRENT_FAN_MODE:

            if value == SA_FAN_MODE_OFF:
                custom_operation = 'off'

                await self.fire_on_update({
                    "custom_operation": custom_operation
                })



    async def _connect(self):
        """Start websocket connection."""
        async with websockets.connect(
                self.url
        ) as websocket:
            self.connection = websocket

            """Send login string."""
            await self.send(login(self.iam, self.password))

            """Run data handler."""
            await self._handler()

        if not self.is_graceful_disconnect:
            await self.fire_events(self.on_disconnect)
        self.is_graceful_disconnect = False

    async def fire_events(self, cbs):
        _ = [await _() for _ in cbs]

    async def fire_on_update(self, data: dict):

        for k, v in data.items():
            try:
                if k == "main_airflow":
                    _LOGGER.info("Received data update: %s => %s" % (k, v))
                v = POSTPROCESS_MAP[k](v)
            except KeyError as e:
                pass

            for cb in self.on_update:

                self.data[k] = v
                await cb(k, v)

        for cb in self.on_update_done:
            await cb(self.data)

    @staticmethod
    def _load_sensors():
        for sensor in [x for x in dir(const) if "SENSOR_" in x]:
            yield getattr(const, sensor)

    async def _handler(self):
        """"Websocket handler which receives messages."""

        async for msg in self.connection:

            try:
                data = json.loads(msg)
            except ValueError as error:
                _LOGGER.error("Message from server is not JSON: %s", error)
                continue

            if data["type"] == "LOGGED_IN":
                _LOGGER.debug("Client connected and authenticated")
                await self.fire_events(self.on_connect)

            elif data["type"] == "READ" and "readValues" in data:
                _LOGGER.debug("readValues: %s", data)
                values = data["readValues"]
                await self.fire_on_update(values)

            elif data["type"] == "VALUE_CHANGED" and "changedValues" in data:
                _LOGGER.debug("changedValues: %s", data)
                values = data["changedValues"]
                await self.fire_on_update(values)

            elif data["type"] == "ERROR":
                _LOGGER.error(data)
                break
            else:
                _LOGGER.warning("The read commend is not implemented correctly: %s", data)
                continue

        if not self.is_graceful_disconnect:
            _LOGGER.error('Connection to WS server was closed!')

    async def send(self, data):
        """Send a message through the websocket channel."""
        if self.connection is None or not self.connection.open:
            _LOGGER.warning("Tried to send query when connection does not exists!")
            return False

        _LOGGER.debug(data)
        await self.connection.send(str(data))

    def get(self, key):
        """Retrieve data from the dictionary."""
        if key not in self.data:
            return None

        return self.data[key]

    async def update_sensors(self):
        """Update available sensors via the API."""
        _LOGGER.debug("Updating sensors: %s" % self.subscribed_sensors)
        await self.send(read(list(self.subscribed_sensors)))

    async def set_temperature(self, value):
        """Set the temperature of the ventilation unit."""
        await self.send(write(main_temperature_offset=int(value * 10)))

    async def set_manual_mode(self):
        """Set the ventilation unit in manual mode."""
        await self.send(write(mode_change_request="1"))

    async def set_crowded_mode(self):
        """Set the ventilation unit in crowded mode."""
        await self.send(write(
            user_mode_crowded_duration=8,
            mode_change_request="2"
        ))

    async def set_refresh_mode(self):
        """Set the ventilation unit in refresh mode."""
        await self.send(write(
            user_mode_refresh_duration=240,
            mode_change_request="3"
        ))

    async def set_fireplace_mode(self):
        """Set the ventilation unit in fireplace mode."""
        await self.send(write(
            user_mode_fireplace_duration=60,
            mode_change_request="4"
        ))

    async def set_holiday_mode(self):
        """Set the ventilation unit in holiday mode."""
        await self.send(write(
            user_mode_holiday_duration=365,
            mode_change_request="6"
        ))

    async def set_auto_mode(self):
        """Set the ventilation unit in auto mode."""
        await self.send(write(mode_change_request="0"))

    async def set_away_mode(self):
        """Set the ventilation unit in away mode."""
        await self.send(write(
            user_mode_away_duration=72,
            mode_change_request="5"
        ))

    async def set_fan_off(self):
        """Set the fan speed to off."""
        await self.send(write(main_airflow="1"))

    async def set_fan_low(self):
        """Set the fan speed to low."""
        await self.send(write(main_airflow="2"))

    async def set_fan_normal(self):
        """Set the fan speed to normal."""
        await self.send(write(main_airflow="3"))

    async def set_fan_high(self):
        """Set the fan speed to high."""
        await self.send(write(main_airflow="4"))

    async def set_operation_mode(self, opmode):

        if opmode == SA_OPERATION_MODE_AUTO:
            await self.set_auto_mode()
        elif opmode == SA_OPERATION_MODE_MANUAL:
            await self.set_manual_mode()
        elif opmode == SA_OPERATION_MODE_CROWDED:
            await self.set_crowded_mode()
        elif opmode == SA_OPERATION_MODE_REFRESH:
            await self.set_refresh_mode()
        elif opmode == SA_OPERATION_MODE_FIREPLACE:
            await self.set_fireplace_mode()
        elif opmode == SA_OPERATION_MODE_HOLIDAY:
            await self.set_holiday_mode()
        elif opmode == SA_OPERATION_MODE_IDLE:
            await self.set_away_mode()

    async def set_fan_mode(self, fan_mode):

        if fan_mode == SA_FAN_MODE_OFF:
            await self.set_fan_off()
        elif fan_mode == SA_FAN_MODE_LOW:
            await self.set_fan_low()
        elif fan_mode == SA_FAN_MODE_MEDIUM:
            await self.set_fan_normal()
        elif fan_mode == SA_FAN_MODE_HIGH:
            await self.set_fan_high()

    async def set(self, k, value):
        if k == SENSOR_TARGET_TEMPERATURE:
            await self.set_temperature(value)
        elif k == SENSOR_MODE_CHANGE_REQUEST:
            await self.set_operation_mode(value)
        elif k == SENSOR_CURRENT_FAN_MODE:
            await self.set_fan_mode(value)
        elif k == SENSOR_CUSTOM_OPERATION:

            if value == SA_OPERATION_MODE_OFF:
                await self.set_manual_mode()
                await self.set_fan_off()
            elif value == SA_OPERATION_MODE_AUTO:
                await self.set_auto_mode()

    def get_current_operation(self):
        if SENSOR_CURRENT_OPERATION not in self.data:
            return None

        if self.data[SENSOR_CURRENT_OPERATION] is None:
            return None

        opcode = int(self.data[SENSOR_CURRENT_OPERATION])

        try:
            return USER_MODE[opcode]
        except KeyError:
            return None

    def subscribe(self, sensor_name):
        self.subscribed_sensors.add(sensor_name)
