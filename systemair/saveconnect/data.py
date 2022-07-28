import logging
import typing

from systemair.saveconnect.models import SaveConnectDevice, SaveConnectRegisterItem, update
from systemair.saveconnect.register import Register, SaveConnectRegistry

_LOGGER = logging.getLogger(__name__)


class SaveConnectData:

    def __init__(self):
        self.devices: typing.Dict[str, SaveConnectDevice] = dict()

    def update_device(self, device_data):
        if device_data["identifier"] not in self.devices:
            self.devices[device_data["identifier"]] = SaveConnectDevice.parse_obj(
                {
                    **device_data,
                    "registry": SaveConnectRegistry()
                }
            )

        else:
            update(self.devices[device_data["identifier"]], device_data)

    def update(self, device_id, data):
        if device_id not in self.devices:
            self.devices[device_id] = SaveConnectDevice.parse_obj({
                "registry": SaveConnectRegistry()
            })

        if "WriteDeviceValues" in data:
            data = data["WriteDeviceValues"]
            if data is None:
                data = []
        elif "GetDeviceView" in data:
            data = data["GetDeviceView"]

            if "dataItems" not in data:
                _LOGGER.error("Could not update due to missing dataItems in the API response.")
                return False
            data = data["dataItems"]

        _LOGGER.debug(f"Found {len(data)} registers for device '{device_id}'... Ignoring unknown registers.")

        parsed_data = {
            Register.map[str(x["register"])]: SaveConnectRegisterItem.parse_obj(x)
            for x in data if str(x["register"]) in Register.map
        }

        _LOGGER.debug(f"Updating {len(parsed_data)} registers for device '{device_id}'...")

        # Update existing registry

        update(self.devices[device_id].registry, parsed_data)

        return True

    def get(self, device_id, key, value=None):
        device_data = self.devices[device_id]
        attrib = Register.map[str(key)]
        register_data = getattr(device_data, attrib)

        if value:
            register_value = register_data[value]
            return register_value

        return register_data
