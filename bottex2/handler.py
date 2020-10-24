import functools
import inspect
from typing import Awaitable, Any, Callable

from bottex2.chat import AbstractChat


ParamsHandler = Callable[..., Awaitable]


class HandlerError(Exception):
    pass


def check_params_handler(handler: ParamsHandler):
    if not callable(handler):
        raise TypeError('Handler must be callable')
    sig = inspect.signature(handler)
    # !!! Refactor this


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


def params_handler(handler: ParamsHandler) -> Handler:
    @functools.wraps(handler)
    async def wrapper(request):
        await handler(**request)
    return wrapper


class HandlerMiddleware(Handler):
    def __init__(self, handler: Handler):
        self.handler = handler

    async def __call__(self, request):
        await self.handler(request)
