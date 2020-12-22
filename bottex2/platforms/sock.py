import asyncio
import json
from typing import AsyncIterator

from bottex2.handler import Request, Response
from bottex2.helpers import aiotools
from bottex2.server import Transport


class SockTransport(Transport):
    def __init__(self, host='127.0.0.1', port='8888'):
        self._host = host
        self._port = port
        self._queue = asyncio.Queue()

    async def _callback(self,
                        reader: asyncio.StreamReader,
                        writer: asyncio.StreamWriter):
        while True:
            data = await reader.readline()
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                pass
            self._queue.put_nowait((writer, data))

    async def listen(self) -> AsyncIterator[Request]:
        server = await asyncio.start_server(self._callback, self._host, self._port)
        aiotools.create_task(server.serve_forever())
        while True:
            event, writer = await self._queue.get()
            yield Request(text=event, raw=event, __writer__=writer)

    async def send(self, request: Request, response: Response):
        sep, sym = '\n\r', '| '
        text = sym + response.text.replace('\n', sep+sym) + sep
        request.__writer__.write(text.encode())
