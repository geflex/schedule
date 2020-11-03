from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Type

from bottex2 import aiotools
from bottex2.chat import ChatMiddleware, AbstractChat
from bottex2.handler import Handler, HandlerMiddleware, Request
from bottex2.logging import logger


class Receiver(ABC):
    _handler: Handler = None
    _wrapped_handler: Handler = None

    def __init__(self):
        super().__init__()
        self.handler_middlewares = []  # type: List[Type[HandlerMiddleware]]
        self.chat_middlewares = []  # type: List[Type[ChatMiddleware]]

    def add_chat_middleware(self, middleware: Type[ChatMiddleware]):
        self.chat_middlewares.append(middleware)

    def wrap_chat(self, chat: AbstractChat):
        for middleware in self.chat_middlewares:
            chat = middleware(chat)
        return chat

    def add_handler_middleware(self, middleware: Type[HandlerMiddleware]):
        self.handler_middlewares.append(middleware)
        self._wrapped_handler = middleware(self._wrapped_handler)

    def wrap_handler(self, handler: Handler):
        for middleware in self.handler_middlewares:
            handler = middleware(handler)
        return handler

    def set_handler(self, handler: Handler) -> Handler:
        """
        Sets handler for this reseiver
        Can be used as a decorator
        """
        self._handler = handler
        self._wrapped_handler = self.wrap_handler(handler)
        return handler

    @abstractmethod
    async def listen(self) -> AsyncIterator[Request]:
        """Recieves and yields events"""
        yield

    def _check(self):
        if self._handler is None:
            logger.warning('Attribute `_handler` was not set. '
                           'You must call `set_handler` or override '
                           '`_handler` in a subclass.')

    async def serve_async(self):
        """
        Receives events from `listen` and handles it in `_handler`.
        Also uses extensions for process events.
        """
        self._check()
        async for request in self.listen():
            handler = self._wrapped_handler
            coro = handler(request)
            aiotools.create_task(coro)

    def serve_forever(self):
        """The blocking version of `serve_async`"""
        aiotools.run_async(self.serve_async())
