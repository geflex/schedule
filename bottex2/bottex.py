import warnings
from typing import Type, Set, Tuple, List, AsyncIterator

from bottex2 import aiotools
from bottex2.chat import ChatMiddleware
from bottex2.handler import Params, HandlerError, Handler, HandlerMiddleware
from bottex2.middlewares import AbstractMiddleware
from bottex2.receiver import Receiver
from bottex2.aiotools import merge_async_iterators


class BottexMiddleware:
    middlewares_receivers: Set[Tuple[AbstractMiddleware, Type[Receiver]]]

    def __init_subclass__(cls, **kwargs):
        cls.middlewares_receivers = set()

    @classmethod
    def submiddleware(cls, receiver: Type[Receiver]):
        def register(middleware: AbstractMiddleware):
            cls.submiddleware_add(receiver, middleware)
            return middleware
        return register

    @classmethod
    def submiddleware_add(cls,
                          receiver: Type[Receiver],
                          middleware: AbstractMiddleware):
        cls.middlewares_receivers.add((middleware, receiver))

    @classmethod
    def get_middleware(cls, receiver: Type[Receiver]) -> AbstractMiddleware:
        for m, c in cls.middlewares_receivers:
            if receiver is c:
                return m
        return cls

    @classmethod
    def get_receiver(cls, middleware: AbstractMiddleware) -> Type[Receiver]:
        for m, c in cls.middlewares_receivers:
            if middleware is m:
                return c
        raise KeyError


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
            warnings.warn(f'No handler middleware specified for '
                          f'{type(receiver).__name__}')
        receiver.add_handler_middleware(submiddleware)

    def _add_chat_middleware(self,
                             receiver: Receiver,
                             middleware: Type[BottexChatMiddleware]):
        submiddleware = middleware.get_middleware(type(receiver))
        if submiddleware is middleware:
            warnings.warn(f'No chat middleware specified for '
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
