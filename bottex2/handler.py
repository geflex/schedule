import inspect
from typing import Awaitable, Any, Callable

from bottex2 import tools
from bottex2.chat import AbstractChat
from bottex2.logging import logger


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
    if not tools.have_kwargs_parameter(handler):
        logger.warning('Handler must have a **kwargs parameter')


class HandlerMiddleware(Handler):
    def __init__(self, handler: Handler):
        self.handler = handler

    async def __call__(self, **params):
        await self.handler(**params)


class Request(Params):
    pass


RequestHandler = Callable[[Request], Awaitable]


def request_handler(handler: RequestHandler) -> Handler:
    async def wrapper(**params):
        request = Request(**params)
        await handler(request)
    return wrapper
