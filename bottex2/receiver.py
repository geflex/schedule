import asyncio
import warnings
from abc import ABC, abstractmethod
from typing import AsyncIterator

from bottex2 import aiotools
from bottex2.handler import Handler, Params
from bottex2.middlewares import MiddlewareContainer, Middleware


class Receiver(MiddlewareContainer, ABC):
    _handler: Handler = None
    _wrapped_handler: Handler = None

    def __init__(self):
        super().__init__()

    def set_handler(self, handler: Handler) -> Handler:
        """
        Sets handler for this reseiver
        Can be used as a decorator
        """
        self._handler = handler
        self._wrapped_handler = self._wrap_into_middlewares(handler)
        return handler

    def add_middleware(self, middleware: Middleware):
        super().add_middleware(middleware)
        self._wrapped_handler = middleware(self._wrapped_handler)

    @abstractmethod
    async def listen(self) -> AsyncIterator[Params]:
        """Recieves and yields events"""
        yield

    def _check(self):
        if self._handler is None:
            warnings.warn('Attribute `_handler` was not set. '
                          'You must call `set_handler` or override '
                          '`_handler` in a subclass.')

    async def serve_async(self):
        """
        Receives events from `listen` and handles it in `_handler`.
        Also uses middlewares for process events.
        """
        self._check()
        async for params in self.listen():
            handler = self._wrapped_handler
            coro = handler(**params)
            aiotools.create_task(coro)

    def serve_forever(self):
        """The blocking version of `serve_async`"""
        aiotools.run_async(self.serve_async())
