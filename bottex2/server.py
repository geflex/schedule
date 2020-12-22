from abc import ABC, abstractmethod
from typing import AsyncIterator, Iterable

from bottex2.handler import Request, ErrorResponse, Handler, Response
from bottex2.helpers import aiotools


class Transport(ABC):
    @abstractmethod
    async def listen(self) -> AsyncIterator[Request]:
        yield

    @abstractmethod
    async def send(self, request: Request, response: Response):
        pass


class Server(ABC):
    def __init__(self, transport: Transport, handler: Handler):
        self._transport = transport
        self._handler = handler

    async def handle(self, request: Request):
        try:
            response = await self._handler(request)
        except ErrorResponse as e:
            response = e.resp
        if isinstance(response, Iterable):
            for resp in response:
                await self.send(request, resp)

    async def serve_async(self):
        async for request in self.listen():
            coro = self.handle(request)
            aiotools.create_task(coro)

    def serve_forever(self):
        """The blocking version of `serve_async`"""
        aiotools.run_async(self.serve_async())

    def listen(self):
        return self._transport.listen()

    def send(self, request: Request, response):
        return self._transport.send(request, response)
