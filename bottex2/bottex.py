from typing import Type, AsyncIterator, Dict, Any, Awaitable, List

from bottex2.handler import HandlerError, HandlerMiddleware, Request
from bottex2.helpers import aiotools
from bottex2.helpers.aiotools import merge_async_iterators
from bottex2.logging import logger
from bottex2.receiver import Receiver


class BottexMiddleware(HandlerMiddleware):
    __unified__ = False


class MiddlewareManager:
    shared: 'MiddlewareManager'

    def __init__(self):
        self.middlewares = {}  # type: Dict[Type[BottexMiddleware], Dict[Type[Receiver], Type[HandlerMiddleware]]]

    def register_child(self,
                       parent: Type[BottexMiddleware],
                       receiver_cls: Type[Receiver],
                       middleware: Type[HandlerMiddleware]):
        children = self.get_children(parent)
        children[receiver_cls] = middleware

    def get_children(self, parent: Type[BottexMiddleware]) -> Dict[Type[Receiver], Type[HandlerMiddleware]]:
        for registered_parent, children in self.middlewares.items():
            if issubclass(parent, registered_parent):
                return children
        children = {}
        self.middlewares[parent] = children
        return children

    def get_child(self,
                  parent: Type[BottexMiddleware],
                  receiver_cls: Type[Receiver]) -> Type[HandlerMiddleware]:
        child = self.get_children(parent).get(receiver_cls)
        if child is None:
            return parent
        return type(child.__name__, (child, parent), {})


MiddlewareManager.shared = MiddlewareManager()


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
            submiddleware = MiddlewareManager.shared.get_child(middleware, type(receiver))
            receiver.add_middleware(submiddleware)

    def add_receiver(self, receiver: Receiver):
        self._receivers.append(receiver)
        for middleware in self.handler_middlewares:
            submiddleware = MiddlewareManager.shared.get_child(middleware, type(receiver))
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
