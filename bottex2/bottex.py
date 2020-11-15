from typing import Type, AsyncIterator, Any, Awaitable, List

from bottex2.handler import HandlerError, HandlerMiddleware, Request
from bottex2.helpers import aiotools
from bottex2.helpers.aiotools import merge_async_iterators
from bottex2.logging import logger
from bottex2.middlewares import MiddlewareManager
from bottex2.receiver import Receiver


class BottexMiddleware(HandlerMiddleware):
    __unified__ = False


middlewares = MiddlewareManager()


class HandlerBottexMiddleware(BottexMiddleware):
    __unified__ = False

    async def __call__(self, request: Request) -> Awaitable[Any]:
        handler = request.__receiver__._handler
        if handler is not None:
            try:
                return await handler(request)
            except HandlerError:  # !!! Maybe NoHandlerError?
                pass
        return await super().__call__(request)


class Bottex(Receiver):
    def __init__(self, *receivers: Receiver):
        super().__init__()
        self._receivers = list(receivers)  # type: List[Receiver]
        self.add_middleware(HandlerBottexMiddleware)

    def add_middleware(self, middleware: Type[BottexMiddleware]):
        super().add_middleware(middleware)
        for receiver in self._receivers:
            submiddleware = middlewares.get_child(middleware, type(receiver))
            receiver.add_middleware(submiddleware)

    def add_receiver(self, receiver: Receiver):
        self._receivers.append(receiver)
        for middleware in self.handler_middlewares:
            submiddleware = middlewares.get_child(middleware, type(receiver))
            receiver.add_middleware(submiddleware)

    async def wrap_receiver(self, receiver: Receiver) -> AsyncIterator[Request]:
        handler = receiver.wrap_handler(self._handler)
        async for request in receiver.listen():
            request = request.copy()
            request.__receiver__ = receiver
            request.__handler__ = handler
            yield request

    async def listen(self) -> AsyncIterator[Request]:
        aiters = [self.wrap_receiver(rcvr) for rcvr in self._receivers]
        logger.info('Bottex listening started')
        async for message in merge_async_iterators(aiters):
            yield message

    async def serve_async(self):
        self._check()
        async for request in self.listen():
            handler = request.__handler__
            coro = handler(request)
            aiotools.create_task(coro)
