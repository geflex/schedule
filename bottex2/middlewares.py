from typing import Awaitable, Iterable, Callable

from bottex2.handler import Handler, Request, TResponse


class HandlerMiddleware(Handler):
    def __init__(self, handler: Handler):
        self._handler = handler
        try:
            self.__name__ = handler.__name__
        except AttributeError:
            pass

    def __call__(self, request: Request) -> Awaitable[TResponse]:
        return self._handler(request)


THandlerMiddleware = Callable[[Handler], Handler]


class WrappedHandler(HandlerMiddleware):
    def __init__(self, handler: Handler, middlewares: Iterable[THandlerMiddleware]):
        super().__init__(handler)
        self._middlewares = middlewares
        self._wrapped_handler = self.wrap_handler(handler)

    def wrap_handler(self, handler: Handler):
        for middleware in self.middlewares:
            handler = middleware(handler)
        return handler

    def __call__(self, request: Request) -> Awaitable[TResponse]:
        return self._wrapped_handler(request)
