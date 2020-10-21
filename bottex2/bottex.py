import warnings
from functools import partial
from typing import Type, Set, List, AsyncIterator, Dict, Optional

from bottex2 import aiotools
from bottex2.chat import ChatMiddleware
from bottex2.handler import Params, HandlerError, Handler, HandlerMiddleware
from bottex2.middlewares.middlewares import AbstractMiddleware
from bottex2.receiver import Receiver
from bottex2.aiotools import merge_async_iterators


class BottexMiddleware:
    @classmethod
    def submiddleware(cls, receiver_cls: Type[Receiver],
                      middleware: Optional[AbstractMiddleware] = None):
        return specify_middleware(cls, receiver_cls, middleware)

    @classmethod
    def get_middleware(cls, receiver_cls: Type[Receiver]) -> AbstractMiddleware:
        return middlewares.setdefault(cls, {}).get(receiver_cls, cls)


middlewares: Dict[Type[BottexMiddleware], Dict[Type[Receiver], AbstractMiddleware]]
middlewares = {}


def specify_middleware(bottex_middleware: Type[BottexMiddleware],
                       receiver_cls: Type[Receiver],
                       middleware: Optional[AbstractMiddleware] = None):
    specified = middlewares.setdefault(bottex_middleware, {})
    if middleware is None:
        return partial(specify_middleware, bottex_middleware, receiver_cls)
    specified[receiver_cls] = middleware


class BottexHandlerMiddleware(BottexMiddleware, HandlerMiddleware):
    pass


class BottexChatMiddleware(BottexMiddleware, ChatMiddleware):
    pass


class ReceiverParams(Params):
    __receiver__: Receiver
    __handler__: Handler


class Bottex(Receiver):
    middlewares: List[BottexHandlerMiddleware]

    def __init__(self, *receivers: Receiver):
        super().__init__()
        self._receivers = set(receivers)  # type: Set[Receiver]

    def _add_handler_middleware(self,
                                receiver: Receiver,
                                middleware: Type[BottexHandlerMiddleware]):
        submiddleware = middleware.get_middleware(type(receiver))
        if submiddleware is middleware:
            warnings.warn(f'No {middleware.__name__} specified for '
                          f'{type(receiver).__name__}')
        receiver.add_handler_middleware(submiddleware)

    def _add_chat_middleware(self,
                             receiver: Receiver,
                             middleware: Type[BottexChatMiddleware]):
        submiddleware = middleware.get_middleware(type(receiver))
        if submiddleware is middleware:
            warnings.warn(f'No {middleware.__name__} specified for '
                          f'{type(receiver).__name__}')
        receiver.add_chat_middleware(submiddleware)

    def add_handler_middleware(self, middleware: Type[BottexHandlerMiddleware]):
        super().add_handler_middleware(middleware)
        for receiver in self._receivers:
            self._add_handler_middleware(receiver, middleware)

    def add_chat_middleware(self, middleware: Type[BottexChatMiddleware]):
        super().add_chat_middleware(middleware)
        for receiver in self._receivers:
            self._add_chat_middleware(receiver, middleware)

    def add_receiver(self, receiver: Receiver):
        self._receivers.add(receiver)
        for middleware in self.handler_middlewares:
            self._add_handler_middleware(receiver, middleware)
        for middleware in self.chat_middlewares:
            self._add_chat_middleware(receiver, middleware)

    async def handle(self, __receiver__, **params):
        if __receiver__._handler is not None:
            try:
                await __receiver__._handler(**params)
                return
            except HandlerError:  # !!! Maybe NoHandlerError?
                pass
        await self._handler(**params)

    async def wrap_receiver(self, receiver: Receiver) -> AsyncIterator[ReceiverParams]:
        handler = receiver.wrap_handler(self.handle)
        async for params in receiver.listen():
            params = params.copy()
            params['__receiver__'] = receiver
            params['__handler__'] = handler
            yield params

    async def listen(self) -> AsyncIterator[ReceiverParams]:
        aiters = [self.wrap_receiver(rcvr) for rcvr in self._receivers]
        async for message in merge_async_iterators(aiters):
            yield message

    async def serve_async(self):
        self._check()
        async for params in self.listen():
            handler = params['__handler__']
            coro = handler(**params)
            aiotools.create_task(coro)
