import asyncio
import warnings
from abc import ABC, abstractmethod
from typing import AsyncIterator

from bottex2 import tools
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

    async def serve_async(self):
        """
        Receives events from `listen` and handles it in `_handler`.
        Also uses middlewares for process events.
        """
        if self._handler is None:
            warnings.warn('Attribute `_handler` was not set. '
                          'You must call `set_handler` or override '
                          '`_handler` in a subclass.')
        async for params in self.listen():
            handler = self._wrapped_handler(**params)
            asyncio.create_task(handler)

    def serve_forever(self):
        """The blocking version of `serve_async`"""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.serve_async())
        tools.run_pending_tasks(loop)
