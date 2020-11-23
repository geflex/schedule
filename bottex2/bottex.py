from typing import Type, AsyncIterator, Any, Awaitable, List, Iterable

from bottex2.handler import HandlerError, HandlerMiddleware, Request, Handler
from bottex2.helpers import aiotools
from bottex2.helpers.aiotools import merge_async_iterators
from bottex2.logging import logger
from bottex2.middlewares import MiddlewareManager
from bottex2.server import Server


class BottexMiddleware(HandlerMiddleware):
    __unified__ = False


manager = MiddlewareManager()


class HandlerBottexMiddleware(BottexMiddleware):
    __unified__ = False

    async def __call__(self, request: Request) -> Awaitable[Any]:
        handler = request.__server__._handler
        if handler is not None:
            try:
                return await handler(request)
            except HandlerError:  # !!! Maybe NoHandlerError?
                pass
        return await super().__call__(request)


class Bottex(Server):
    def __init__(self,
                 handler: Handler,
                 middlewares: Iterable[Type[HandlerMiddleware]] = (),
                 servers: Iterable[Server] = (),
                 middleware_manager=manager):
        self.middleware_manager = middleware_manager
        self._servers = list(servers)  # type: List[Server]
        middlewares = [HandlerBottexMiddleware] + list(middlewares)
        super().__init__(handler, middlewares)

    def add_middleware(self, middleware: Type[BottexMiddleware]):
        super().add_middleware(middleware)
        for server in self._servers:
            submiddleware = self.middleware_manager.get_child(middleware, type(server))
            server.add_middleware(submiddleware)

    def add_server(self, server: Server):
        self._servers.append(server)
        for middleware in self.handler_middlewares:
            submiddleware = self.middleware_manager.get_child(middleware, type(server))
            server.add_middleware(submiddleware)

    async def wrap_server(self, server: Server) -> AsyncIterator[Request]:
        handler = server.wrap_handler(self._handler)
        async for request in server.listen():
            request = request.copy()
            request.__server__ = server
            request.__handler__ = handler
            yield request

    async def listen(self) -> AsyncIterator[Request]:
        aiters = [self.wrap_server(rcvr) for rcvr in self._servers]
        logger.info('Bottex listening started')
        async for message in merge_async_iterators(aiters):
            yield message

    async def serve_async(self):
        async for request in self.listen():
            handler = request.__handler__
            coro = handler(request)
            aiotools.create_task(coro)
