from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import AsyncIterator, Optional

from bottex2 import multiplatform
from bottex2.ext.users import UserMiddleware
from bottex2.handler import Request
from bottex2.keyboard import Keyboard
from bottex2.server import Transport


@dataclass
class PyMessage:
    text: str
    queue: asyncio.Queue[PyMessage]
    response_id: int = None


class PyTransport(Transport):
    def __init__(self):
        self._last_id = 0
        self._queue = asyncio.Queue()  # type: asyncio.Queue[PyMessage]

    async def recv(self, obj: PyMessage):
        await self._queue.put(obj)

    def recv_nowait(self, obj: PyMessage):
        self._queue.put_nowait(obj)

    async def listen(self) -> AsyncIterator[Request]:
        while True:
            message = await self._queue.get()
            yield Request(text=message.text, raw=message, )

    async def send(self, request: Request,
                   text: Optional[str] = None,
                   kb: Optional[Keyboard] = None):
        await request.raw.queue.put(PyMessage(text, self._queue, request.raw.response_id))


class PyUserMiddleware(UserMiddleware):
    def get_user(self, request: Request):
        return self.get_or_create('py', 'default')


multiplatform.manager.register_child(UserMiddleware, PyTransport, PyUserMiddleware)
