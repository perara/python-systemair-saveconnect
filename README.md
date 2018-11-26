# python-systemair-savecair

This is a simple package that expose the savecair API as a python module.

# Installation
```python
pip install python-systemair-savecair
```

# Example
```python
from systemair.savecair.client import SavecairClient
import asyncio
if __name__ == "__main__":

    async def on_connect():
        pass

    async def on_disconnect():
        pass

    async def on_update():
        pass

    async def on_error():
        pass

    async def start(loop=asyncio.get_event_loop()):
        x = SavecairClient(iam_id="xxxxx", password="xxxxx", loop=loop)
        x.on_connect.append(on_connect)
        x.on_disconnect.append(on_disconnect)
        x.on_update.append(on_update)
        x.on_error.append(on_error)

        x.start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start(loop))
    loop.run_forever()
```

# Version History
1.0.0 - Initial Version