from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import AsyncIterator, Optional

from bottex2 import users
from bottex2.handler import Params
from bottex2.receiver import Receiver
from bottex2.chat import Chat, Keyboard


@dataclass
class PyMessage:
    text: str
    queue: asyncio.Queue[PyMessage]


class PyChat(Chat):
    def __init__(self, chat_queue, recv_queue):
        self._callback_queue = chat_queue  # type: asyncio.Queue[PyMessage]
        self._recv_queue = recv_queue  # type: asyncio.Queue[PyMessage]

    async def send_message(self, text: Optional[str] = None, kb: Optional[Keyboard] = None):
        await self._callback_queue.put(PyMessage(text, self._recv_queue))


class PyReceiver(Receiver):
    def __init__(self):
        super().__init__()
        self._queue = asyncio.Queue()  # type: asyncio.Queue[PyMessage]

    async def recv(self, obj: PyMessage):
        await self._queue.put(obj)

    def recv_nowait(self, obj: PyMessage):
        self._queue.put_nowait(obj)

    async def listen(self) -> AsyncIterator[Params]:
        while True:
            obj = await self._queue.get()
            yield Params(text=obj.text,
                         chat=PyChat(obj.queue, self._queue),
                         raw=obj)


@users.middleware_for(PyReceiver)
def sock_user_middleware(handler):
    async def middleware(raw: PyMessage, **params):
        user = await users.user_model.get('py', 'default')
        await handler(user=user, raw=raw, **params)
    return middleware
