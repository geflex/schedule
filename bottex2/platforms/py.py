from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import AsyncIterator, Optional, Type, Iterable

from bottex2 import bottex
from bottex2.chat import AbstractChat, Keyboard
from bottex2.ext.users import UserBottexMiddleware
from bottex2.handler import Request, HandlerMiddleware, Handler
from bottex2.server import Server


@dataclass
class PyMessage:
    text: str
    queue: asyncio.Queue[PyMessage]
    response_id: int = None


class PyChat(AbstractChat):
    def __init__(self, callback_queue, recv_queue, message_id):
        self._callback_queue = callback_queue  # type: asyncio.Queue[PyMessage]
        self._recv_queue = recv_queue  # type: asyncio.Queue[PyMessage]
        self._message_id = message_id

    async def send_message(self, text: Optional[str] = None, kb: Optional[Keyboard] = None):
        await self._callback_queue.put(PyMessage(text, self._recv_queue, self._message_id))


class PyServer(Server):
    def __init__(self, handler: Handler, middlewares: Iterable[Type[HandlerMiddleware]] = ()):
        super().__init__(handler, middlewares)
        self._last_id = 0
        self._queue = asyncio.Queue()  # type: asyncio.Queue[PyMessage]

    async def recv(self, obj: PyMessage):
        await self._queue.put(obj)

    def recv_nowait(self, obj: PyMessage):
        self._queue.put_nowait(obj)

    async def listen(self) -> AsyncIterator[Request]:
        while True:
            message = await self._queue.get()
            chat = PyChat(message.queue, self._queue, message.response_id)
            yield Request(text=message.text,
                          chat=chat,
                          raw=message)


class PyUserHandlerMiddleware(UserBottexMiddleware):
    async def get_user(self, request: Request):
        return await self.get_or_create('py', 'default')


bottex.manager.register_child(UserBottexMiddleware, PyServer, PyUserHandlerMiddleware)
