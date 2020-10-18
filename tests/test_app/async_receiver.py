import json
from typing import AsyncIterator, Optional
import asyncio

from bottex2.chat import Chat, Keyboard
from bottex2.handler import Params
from bottex2.receiver import Receiver


class AsyncChat(Chat):
    async def send_message(self,
                           text: Optional[str] = None,
                           kb: Optional[Keyboard] = None):
        self._writer.write(bytes(text))

    def __init__(self, writer: asyncio.StreamWriter):
        self._writer = writer


class AsyncRecv(Receiver):
    def __init__(self, host='127.0.0.1', port=8888):
        super().__init__()
        self._host = host
        self._port = port

    async def listen(self) -> AsyncIterator[Params]:
        queue = asyncio.Queue()
        async def _callback(reader: asyncio.StreamReader,
                            writer_: asyncio.StreamWriter):
            data = await reader.readline()
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                pass
            queue.put_nowait((writer_, data))

        while True:
            writer, event = await queue.get()
            yield {
                'text': event,
                'chat': AsyncChat(writer),
                'raw': event
            }
