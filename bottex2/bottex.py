import warnings
from typing import Type, Set, Iterable, Tuple, AsyncIterator, List, Collection

from bottex2.handler import Params, HandlerError, Handler
from bottex2.middlewares import Middleware, MiddlewareContainer
from bottex2.receiver import Receiver
from bottex2.tools import merge_async_iterators2


class MiddlewareAggregator(Handler):
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
    def deferred_add_middleware(cls, container: Type[MiddlewareContainer], middleware: Middleware):
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
                    warnings.warn(f'No specific middleware registered for {type(container).__name__}')
            container.add_middleware(middleware)

    def __init__(self, handler: Handler):
        self.handler = handler

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

    def add_middleware(self, aggregator: Type[MiddlewareAggregator], *, add_specific=True):
        super().add_middleware(aggregator)
        aggregator.add_to_all(self._receivers, only_default=(not add_specific))

    async def handle(self, __receiver__, **params):
        if __receiver__._handler is not None:
            try:
                await __receiver__._handler(**params)
                return
            except HandlerError:  # Maybe NoHandlerError?
                pass
        await self._handler(**params)

    async def listen(self) -> AsyncIterator[ReceiverParams]:
        async def _wrapper(receiver: Receiver) -> AsyncIterator[ReceiverParams]:
            handler = receiver._wrap_into_middlewares(self.handle)
            async for params in receiver.listen():
                params = params.copy()
                # noinspection PyTypeChecker
                params['__receiver__'] = receiver
                # noinspection PyTypeChecker
                params['__handler__'] = handler
                yield params

        aiters = [_wrapper(rcvr) for rcvr in self._receivers]
        async for message in merge_async_iterators2(aiters):
            yield message

    async def _serve_async(self):
        async for params in self.listen():
            handler = params['__handler__']
            task = handler(**params)
            self.multitask.add(task)
