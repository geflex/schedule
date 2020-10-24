import functools
import inspect
from typing import Awaitable, Any, Callable

from bottex2.chat import AbstractChat
from bottex2.logging import logger


class HandlerError(Exception):
    pass


class Request(dict):
    text: str
    chat: AbstractChat
    raw: Any

    def __init__(self, *, text: str, chat: AbstractChat, raw: Any, **params):
        super().__init__(text=text, chat=chat, raw=raw, **params)

    def __getattr__(self, attr):
        return self[attr]

    def copy(self):
        return Request(**self)


Handler = Callable[[Request], Awaitable]


def check_handler(handler: Handler):
    if not callable(handler):
        raise TypeError('Handler must be callable')
    sig = inspect.signature(handler)
    if len(sig.parameters) > 1:
        logger.warning('Handler must accept only one argument')


class HandlerMiddleware(Handler):
    def __init__(self, handler: Handler):
        self.handler = handler

    async def __call__(self, request):
        await self.handler(request)


ParamsHandler = Callable[..., Awaitable]


def params_handler(handler: ParamsHandler) -> Handler:
    @functools.wraps(handler)
    async def wrapper(request):
        await handler(**request)
    return wrapper
