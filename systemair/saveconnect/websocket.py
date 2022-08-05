import asyncio
import logging
import socket

import websockets
from websockets.exceptions import InvalidStatusCode

logger = logging.getLogger(__name__)


class WSClient:

    def __init__(self, saveconnect, url, loop=asyncio.get_event_loop(), **kwargs):
        self.url = url
        self.saveconnect = saveconnect
        self.ws = None
        self._access_token = None
        self.loop = loop
        # set some default values
        self.reply_timeout = kwargs.get('reply_timeout') or 10
        self.ping_timeout = kwargs.get('ping_timeout') or 5
        self.sleep_time = kwargs.get('sleep_time') or 5
        self.callback = kwargs.get('callback')

    def set_callback(self, cb):
        self.callback = cb

    async def connect(self):
        self.loop.create_task(self.listen_forever())

        while not self.ws:
            await asyncio.sleep(0.1)

    def set_access_token(self, token):
        self._access_token = token["access_token"]

    def is_connected(self):
        return self.ws is not None

    async def listen_forever(self):
        while True:
            # outer loop restarted every time the connection fails
            logger.debug('Creating new connection...')
            try:

                async with websockets.connect(
                        self.url,
                        subprotocols=['accessToken', self._access_token]) as ws:
                    self.ws = ws
                    while True:
                        # listener loop
                        try:
                            reply = await asyncio.wait_for(ws.recv(), timeout=self.reply_timeout)
                        except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed):
                            try:
                                pong = await ws.ping()
                                await asyncio.wait_for(pong, timeout=self.ping_timeout)
                                # logger.debug('Ping OK, keeping connection alive...')
                                continue
                            except:
                                logger.debug(
                                    'Ping error - retrying connection in {} sec...'.format(
                                        self.sleep_time))
                                await asyncio.sleep(self.sleep_time)
                                break
                        logger.debug('Server said > {}'.format(reply))
                        if self.callback:
                            await self.callback(reply)
            except socket.gaierror:
                self.ws = None
                logger.debug(
                    'Socket error - retrying connection in {} sec...'.format(self.sleep_time))
                await asyncio.sleep(self.sleep_time)
                continue
            except ConnectionRefusedError:
                self.ws = None
                logger.debug('Nobody seems to listen to this endpoint. Please check the URL.')
                logger.debug('Retrying connection in {} sec...'.format(self.sleep_time))
                await asyncio.sleep(self.sleep_time)
                continue
            except InvalidStatusCode as e:
                self.ws = None
                logger.error(f"Could not connect to the websocket API. Go code: {e.status_code}")

                if e.status_code == 401:
                    # Unauthorized
                    await self.saveconnect.refresh_token()

                await asyncio.sleep(self.sleep_time)
