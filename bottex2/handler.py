import inspect
import warnings
from typing import Awaitable, Any, Callable

from bottex2 import tools
from bottex2.chat import Chat


class Params(dict):
    def __init__(self, *, text: str, chat: Chat, raw: Any):
        super().__init__(text=text, chat=chat, raw=raw)

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
        warnings.warn('Handler must have a **kwargs parameter')


class HandlerMiddleware(Handler):
    def __init__(self, handler: Handler):
        self.handler = handler

    async def __call__(self, **params):
        await self.handler(**params)
