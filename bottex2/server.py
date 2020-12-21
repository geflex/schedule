from abc import ABC, abstractmethod
from typing import AsyncIterator, Iterable, Optional, Awaitable

from bottex2.handler import Request, ErrorResponse, Handler, TResponse
from bottex2.helpers import aiotools
from bottex2.keyboard import Keyboard


class AbstractServer(ABC):
    @abstractmethod
    async def listen(self) -> AsyncIterator[Request]:
        yield

    @abstractmethod
    async def _handle(self, request: Request) -> TResponse:
        pass

    @abstractmethod
    async def send(self, request: Request,
                   text: Optional[str] = None,
                   kb: Optional[Keyboard] = None):
        pass

    async def handle(self, request: Request):
        try:
            response = await self._handle(request)
        except ErrorResponse as e:
            response = e.resp
        if isinstance(response, Iterable):
            for resp in response:
                await self.send(request, resp.text, resp.kb)

    async def serve_async(self):
        async for request in self.listen():
            coro = self.handle(request)
            aiotools.create_task(coro)

    def serve_forever(self):
        """The blocking version of `serve_async`"""
        aiotools.run_async(self.serve_async())


class Transport(ABC):
    @abstractmethod
    async def listen(self) -> AsyncIterator[Request]:
        yield

    @abstractmethod
    async def send(self, request: Request,
                   text: Optional[str] = None,
                   kb: Optional[Keyboard] = None):
        pass


class Server(AbstractServer, ABC):
    def __init__(self, transport: Transport, handler: Handler):
        self._transport = transport
        self._handler = handler

    def _handle(self, request: Request) -> Awaitable[TResponse]:
        return self._handler(request)

    def listen(self):
        return self._transport.listen()

    def send(self, request: Request,
                   text: Optional[str] = None,
                   kb: Optional[Keyboard] = None):
        return self._transport.send(request, text, kb)
