from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Type, Iterable

from bottex2.handler import Handler, HandlerMiddleware, Request
from bottex2.helpers import aiotools


def sender(handler: Handler) -> Handler:
    async def wrapper(self, request: Request):
        response = await handler(request)
        if isinstance(response, Iterable):
            for resp in response:
                await request.chat.send_message(resp.text, resp.kb)
    return wrapper


class Server(ABC):
    def __init__(self, handler: Handler,
                 middlewares: Iterable[Type[HandlerMiddleware]] = ()):
        self.handler_middlewares = []  # type: List[Type[HandlerMiddleware]]
        self._handler = None
        self._wrapped_handler = None
        for middleware in middlewares:
            self.add_middleware(middleware)
        self.set_handler(handler)

    def add_middleware(self, middleware: Type[HandlerMiddleware]):
        self.handler_middlewares.append(middleware)
        self._wrapped_handler = middleware(self._wrapped_handler)

    def wrap_handler(self, handler: Handler):
        for middleware in self.handler_middlewares:
            handler = middleware(handler)
        return sender(handler)

    def set_handler(self, handler: Handler) -> Handler:
        self._handler = handler
        self._wrapped_handler = self.wrap_handler(handler)
        return handler

    @abstractmethod
    async def listen(self) -> AsyncIterator[Request]:
        """Receives and yields events"""
        yield

    async def serve_async(self):
        """
        Receives events from `listen` and handles it in `_handler`.
        Also uses extensions for process events.
        """
        async for request in self.listen():
            handler = self._wrapped_handler
            coro = handler(request)
            aiotools.create_task(coro)

    def serve_forever(self):
        """The blocking version of `serve_async`"""
        aiotools.run_async(self.serve_async())
