from typing import Type, AsyncIterator, List, Iterable, Dict, Awaitable

from sqlalchemy import Column, Integer, String

from bottex2.handler import Request, Handler, TResponse, Response
from bottex2.helpers.aiotools import merge_async_iterators
from bottex2.logging import logger
from bottex2.middlewares import THandlerMiddleware, HandlerMiddleware
from bottex2.server import Transport


class MultiplatformMiddleware(HandlerMiddleware):
    __unified__ = False


class MultiplatformRequest(Request):
    __transport__: Transport


class MultiplatformTransport(Transport):
    def __init__(self, transports: Iterable[Transport] = ()):
        self._transports = list(transports)  # type: List[Transport]

    async def listener_wrapper(self, transport: Transport) -> AsyncIterator[MultiplatformRequest]:
        async for request in transport.listen():
            request.__transport__ = transport
            yield request

    async def listen(self) -> AsyncIterator[MultiplatformRequest]:
        aiters = [self.listener_wrapper(rcvr) for rcvr in self._transports]
        logger.info('Multiplatform listening started')
        async for message in merge_async_iterators(aiters):
            yield message

    async def send(self, request: MultiplatformRequest, response: Response):
        await request.__transport__.send(request, response)


class MiddlewareManager:
    def __init__(self):
        self.middlewares = {}  # type: Dict[THandlerMiddleware, Dict[Type[Transport], THandlerMiddleware]]

    def register_child(self,
                       parent: THandlerMiddleware,
                       transport: Type[Transport],
                       middleware: THandlerMiddleware):
        children = self.get_children(parent)
        children[transport] = middleware

    def get_children(self, parent: THandlerMiddleware) -> Dict[Type[Transport], THandlerMiddleware]:
        for registered_parent, children in self.middlewares.items():
            if issubclass(parent, registered_parent):
                return children
        children = {}
        self.middlewares[parent] = children
        return children

    def get_child(self, parent_cls: THandlerMiddleware,
                  transport: Type[Transport]) -> THandlerMiddleware:
        child_cls = self.get_children(parent_cls).get(transport)
        if child_cls is None:
            return parent_cls
        # noinspection PyTypeChecker
        return type(child_cls.__name__, (child_cls, parent_cls), {})


manager = MiddlewareManager()


class MultiplatformWrappedHandler(HandlerMiddleware):
    def __init__(self, handler: Handler,
                 middlewares: Iterable[THandlerMiddleware],
                 middleware_manager=manager):
        super().__init__(handler)
        self._handler = handler
        self._middlewares = list(middlewares)
        self._manager = manager

    def wrap_handler(self, transport: Type[Transport]) -> Handler:
        handler = self._handler
        for middleware in self._middlewares:
            wrapper = self._manager.get_child(middleware, transport)
            handler = wrapper(handler)
        return handler

    def __call__(self, request: Request) -> Awaitable[TResponse]:
        transport = request.__transport__
        handler = self.wrap_handler(type(transport))
        return handler(request)


class MultiplatformUserMixin:
    uid = Column(Integer, primary_key=True)
    platform = Column(String)