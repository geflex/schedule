import json
from typing import AsyncIterator, Optional
import asyncio

from bottex2 import aiotools
from bottex2.chat import AbstractChat, Keyboard
from bottex2.handler import Request
from bottex2.receiver import Receiver


def utf_bytes(s):
    return bytes(s, 'utf-8')


class SockChat(AbstractChat):
    async def send_message(self,
                           text: Optional[str] = None,
                           kb: Optional[Keyboard] = None):
        sep, sym = '\n\r', '| '
        text = sym + text.replace('\n', sep+sym) + sep
        b = utf_bytes(text)
        self._writer.write(b)

    def __init__(self, writer: asyncio.StreamWriter):
        self._writer = writer


class SockReciever(Receiver):
    def __init__(self, host='127.0.0.1', port='8888'):
        super().__init__()
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
            chat = SockChat(writer)
            yield Request(text=event,
                          chat=self.wrap_chat(chat),
                          raw=event)
