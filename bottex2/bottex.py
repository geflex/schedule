import warnings
from typing import Type, Set, Iterable, Tuple, AsyncIterator, List

from bottex2 import aiotools
from bottex2.handler import Params, HandlerError, Handler
from bottex2.middlewares import Middleware, MiddlewareContainer, HandlerMiddleware
from bottex2.receiver import Receiver
from bottex2.aiotools import merge_async_iterators


class MiddlewareAggregator(HandlerMiddleware):
    specific_middlewares: Set[Tuple[Middleware, Type[MiddlewareContainer]]]

    def __init_subclass__(cls, **kwargs):
        cls.specific_middlewares = set()

    @classmethod
    def deferred_add(cls, container: Type[MiddlewareContainer]):
        def register(middleware: Middleware):
            cls.deferred_add_middleware(container, middleware)
            return middleware
        return register

    @classmethod
    def deferred_add_middleware(cls,
                                container: Type[MiddlewareContainer],
                                middleware: Middleware):
        cls.specific_middlewares.add((middleware, container))

    @classmethod
    def get_middleware(cls, container: Type[MiddlewareContainer]) -> Middleware:
        for m, c in cls.specific_middlewares:
            if container is c:
                return m
        return cls

    @classmethod
    def get_container(cls, middleware: Middleware) -> Type[MiddlewareContainer]:
        for m, c in cls.specific_middlewares:
            if middleware is m:
                return c
        raise KeyError

    @classmethod
    def add_to_all(cls, containers: Iterable[MiddlewareContainer], *, only_default=False):
        for container in containers:
            if only_default:
                middleware = cls
            else:
                middleware = cls.get_middleware(type(container))
                if middleware is cls:
                    warnings.warn(f'No specific middleware registered for '
                                  f'{type(container).__name__}')
            container.add_middleware(middleware)

    async def __call__(self, **params):
        await self.handler(**params)


class ReceiverParams(Params):
    __receiver__: Receiver
    __handler__: Handler


class Bottex(Receiver):
    middlewares: List[MiddlewareAggregator]

    def __init__(self, *receivers: Receiver):
        super().__init__()
        self._receivers = set(receivers)  # type: Set[Receiver]

    def add_middleware(self, aggregator: Type[MiddlewareAggregator]):
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
