import functools
import inspect
from typing import Awaitable, Any, Callable

from bottex2.chat import AbstractChat


class Params(dict):
    text: str
    chat: AbstractChat
    raw: Any

    def __init__(self, *, text: str, chat: AbstractChat, raw: Any, **params):
        super().__init__(text=text, chat=chat, raw=raw, **params)

    def __getattr__(self, attr):
        return self[attr]


Handler = Callable[..., Awaitable]


class HandlerError(Exception):
    pass


def check_handler(handler: Handler):
    if not callable(handler):
        raise TypeError('Handler must be callable')
    sig = inspect.signature(handler)
    # !!! Refactor this


class Request(Params):
    def copy(self):
        return Request(**self)


RequestHandler = Callable[[Request], Awaitable]


def request_handler(handler: RequestHandler) -> Handler:
    """Back capability"""
    return handler


def params_handler(handler: Handler) -> RequestHandler:
    @functools.wraps(handler)
    async def wrapper(request):
        await handler(**request)
    return wrapper


class HandlerMiddleware(RequestHandler):
    def __init__(self, handler: RequestHandler):
        self.handler = handler

    async def __call__(self, request):
        await self.handler(request)
