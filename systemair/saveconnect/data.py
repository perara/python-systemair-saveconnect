
class SaveConnectData:

    def __init__(self):
        self._data = dict()

    def update(self, device_id, data):
        if device_id not in self._data:
            self._data[device_id] = {}

        if "WriteDeviceValues" in data:
            data = data["WriteDeviceValues"]
        elif "GetDeviceView" in data:
            data = data["GetDeviceView"]["dataItems"]

        for item in data:
            register_id = item["register"]
            self._data[device_id][register_id] = item

    def get(self, device_id, key, value=None):
        device_data = self._data[device_id]
        register_data = device_data[key]

        if value:
            register_value = register_data[value]
            return register_value

        return register_data
