from functools import partial
from typing import Type, Set, List, AsyncIterator, Dict, Optional

from bottex2.handler import HandlerError, Handler, HandlerMiddleware, Request
from bottex2.helpers import aiotools
from bottex2.helpers.aiotools import merge_async_iterators
from bottex2.logging import logger
from bottex2.middlewares import AbstractMiddleware
from bottex2.receiver import Receiver


class BottexMiddleware(HandlerMiddleware):
    __universal__ = False

    @classmethod
    def submiddleware(cls, receiver_cls: Type[Receiver],
                      middleware: Optional[AbstractMiddleware] = None):
        return specify_middleware(cls, receiver_cls, middleware)


def _get_submiddleware(bottex_middleware: Type[BottexMiddleware],
                       receiver_cls: Type[Receiver]) -> AbstractMiddleware:
    return middlewares.setdefault(bottex_middleware, {}).get(receiver_cls, bottex_middleware)


def get_submiddleware(middleware: Type[BottexMiddleware],
                      receiver: Receiver) -> AbstractMiddleware:
    submiddleware = _get_submiddleware(middleware, type(receiver))
    if submiddleware is middleware and not middleware.__universal__:  # !!! __universal__?
        logger.debug(f'No {middleware.__name__} specified for '
                     f'{type(receiver).__name__}')
    return submiddleware


middlewares: Dict[Type[BottexMiddleware], Dict[Type[Receiver], AbstractMiddleware]]
middlewares = {}


def specify_middleware(bottex_middleware: Type[BottexMiddleware],
                       receiver_cls: Type[Receiver],
                       middleware: Optional[AbstractMiddleware] = None):
    specified = middlewares.setdefault(bottex_middleware, {})
    if middleware is None:
        return partial(specify_middleware, bottex_middleware, receiver_cls)
    specified[receiver_cls] = middleware
    return middleware


class ReceiverRequest(Request):
    __receiver__: Receiver
    __handler__: Handler


class Bottex(Receiver):
    middlewares: List[BottexMiddleware]

    def __init__(self, *receivers: Receiver):
        super().__init__()
        self._receivers = set(receivers)  # type: Set[Receiver]

    def add_middleware(self, middleware: Type[BottexMiddleware]):
        super().add_middleware(middleware)
        for receiver in self._receivers:
            submiddleware = get_submiddleware(middleware, receiver)
            receiver.add_middleware(submiddleware)

    def add_receiver(self, receiver: Receiver):
        self._receivers.add(receiver)
        for middleware in self.handler_middlewares:
            submiddleware = get_submiddleware(middleware, receiver)
            receiver.add_middleware(submiddleware)

    async def handle(self, request: Request):
        handler = request.__receiver__._handler
        if handler is not None:
            try:
                await handler(request)
                return
            except HandlerError:  # !!! Maybe NoHandlerError?
                pass
        await self._handler(request)

    async def wrap_receiver(self, receiver: Receiver) -> AsyncIterator[ReceiverRequest]:
        handler = receiver.wrap_handler(self.handle)
        async for request in receiver.listen():
            request = request.copy()
            request.__receiver__ = receiver
            request.__handler__ = handler
            yield request

    async def listen(self) -> AsyncIterator[ReceiverRequest]:
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
