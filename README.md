# python-systemair-saveconnect

This is a simple package that expose the SaveConnect API as a python module.

# Installation
```python
pip install python-systemair-saveconnect
```

# Example

```python
from systemair.saveconnect import SaveConnect
email = ""
password = ""

sc = SaveConnect(
    email=email,
    password=password,
    ws_enabled=True,
    update_interval=60,
    refresh_token_interval=300
)

# Authenticate
if not await sc.login():
    raise RuntimeError("Could not connect to systemAIR")

# Refresh Token
await sc.auth.refresh_token()

devices = await sc.get_devices()
device_0 = devices[0]["identifier"]

device_0_data = await sc.read_data(device_id=device_0)
```

# Version History
* 3.0.0 - Updated to work with SaveConnect
* 1.0.0 - Initial Version
