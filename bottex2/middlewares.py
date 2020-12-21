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


def check_middleware(middleware):
    if not callable(middleware):
        raise TypeError('middleware must be callable')


class WrappedHandler(HandlerMiddleware):
    def __init__(self, handler: Handler, middlewares: Iterable[THandlerMiddleware]):
        super().__init__(handler)
        self._wrapped_handler = handler
        for middleware in middlewares:
            self._wrapped_handler = middleware(handler)

    def __call__(self, request: Request) -> Awaitable[TResponse]:
        return self._wrapped_handler(request)
