import warnings
from typing import Type, Set, Iterable, Tuple, List, AsyncIterator

from bottex2 import aiotools
from bottex2.handler import Params, HandlerError, Handler, HandlerMiddleware
from bottex2.middlewares import AbstractMiddleware, Middlewarable
from bottex2.receiver import Receiver
from bottex2.aiotools import merge_async_iterators


class BottexHandlerMiddleware(HandlerMiddleware):
    middlewares_owners: Set[Tuple[AbstractMiddleware, Type[Middlewarable]]]

    def __init_subclass__(cls, **kwargs):
        cls.middlewares_owners = set()

    @classmethod
    def submiddleware(cls, owner: Type[Middlewarable]):
        def register(middleware: AbstractMiddleware):
            cls.submiddleware_add(owner, middleware)
            return middleware
        return register

    @classmethod
    def submiddleware_add(cls,
                          owner: Type[Middlewarable],
                          middleware: AbstractMiddleware):
        cls.middlewares_owners.add((middleware, owner))

    @classmethod
    def get_middleware(cls, owner: Type[Middlewarable]) -> AbstractMiddleware:
        for m, c in cls.middlewares_owners:
            if owner is c:
                return m
        return cls

    @classmethod
    def get_owner(cls, middleware: AbstractMiddleware) -> Type[Middlewarable]:
        for m, c in cls.middlewares_owners:
            if middleware is m:
                return c
        raise KeyError

    @classmethod
    def add_to_all(cls, owners: Iterable[Middlewarable], *, only_default=False):
        for container in owners:
            if only_default:
                middleware = cls
            else:
                middleware = cls.get_middleware(type(container))
                if middleware is cls:
                    warnings.warn(f'No specific middleware registered for '
                                  f'{type(container).__name__}')
            container.add_middleware(middleware)


class ReceiverParams(Params):
    __receiver__: Receiver
    __handler__: Handler


class Bottex(Receiver):
    middlewares: List[BottexHandlerMiddleware]

    def __init__(self, *receivers: Receiver):
        super().__init__()
        self._receivers = set(receivers)  # type: Set[Receiver]

    def add_middleware(self, aggregator: Type[BottexHandlerMiddleware]):
        super().add_middleware(aggregator)
        aggregator.add_to_all(self._receivers, only_default=False)

    def add_receiver(self, receiver: Receiver):
        self._receivers.add(receiver)
        for middleware in self.middlewares:
            middleware.add_to_all([receiver], only_default=False)

    async def handle(self, __receiver__, **params):
        if __receiver__._handler is not None:
            try:
                await __receiver__._handler(**params)
                return
            except HandlerError:  # !!! Maybe NoHandlerError?
                pass
        await self._handler(**params)

    async def wrap_receiver(self, receiver: Receiver) -> AsyncIterator[ReceiverParams]:
        handler = receiver._wrap_into_middlewares(self.handle)
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
