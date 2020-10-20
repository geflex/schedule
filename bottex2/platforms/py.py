from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import AsyncIterator, Optional

from bottex2 import users
from bottex2.handler import Params, HandlerMiddleware
from bottex2.receiver import Receiver
from bottex2.chat import Chat, Keyboard


@dataclass
class PyMessage:
    text: str
    queue: asyncio.Queue[PyMessage]
    response_id: int = None


class PyChat(Chat):
    def __init__(self, callback_queue, recv_queue, message_id):
        self._callback_queue = callback_queue  # type: asyncio.Queue[PyMessage]
        self._recv_queue = recv_queue  # type: asyncio.Queue[PyMessage]
        self._message_id = message_id

    async def send_message(self, text: Optional[str] = None, kb: Optional[Keyboard] = None):
        await self._callback_queue.put(PyMessage(text, self._recv_queue, self._message_id))


class PyReceiver(Receiver):
    def __init__(self):
        super().__init__()
        self._last_id = 0
        self._queue = asyncio.Queue()  # type: asyncio.Queue[PyMessage]

    async def recv(self, obj: PyMessage):
        await self._queue.put(obj)

    def recv_nowait(self, obj: PyMessage):
        self._queue.put_nowait(obj)

    async def listen(self) -> AsyncIterator[Params]:
        while True:
            message = await self._queue.get()
            chat = PyChat(message.queue, self._queue, message.response_id)
            yield Params(text=message.text,
                         chat=self.wrap_chat(chat),
                         raw=message)


@users.UserBottexHandlerMiddleware.submiddleware(PyReceiver)
class PyUserHandlerMiddleware(HandlerMiddleware):
    async def __call__(self, raw: PyMessage, **params):
        user = await users.user_model.get('py', 'default')
        await self.handler(user=user, raw=raw, **params)
