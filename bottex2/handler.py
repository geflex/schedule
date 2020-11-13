import functools
import inspect
from dataclasses import dataclass
from typing import Awaitable, Any, Callable, Optional, Iterable

from bottex2.chat import AbstractChat, Keyboard
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


@dataclass
class Message:
    text: Optional[str]
    kb: Optional[Keyboard]

    def __iter__(self):
        yield self


Handler = Callable[[Request], Awaitable[Iterable[Message]]]


def check_handler(handler: Handler):
    if not callable(handler):
        raise TypeError('Handler must be callable')
    sig = inspect.signature(handler)
    if len(sig.parameters) > 1:
        logger.warning('Handler must accept only one argument')


class HandlerMiddleware(Handler):
    def __init__(self, handler: Handler):
        self.handler = handler
        try:
            self.__name__ = handler.__name__
        except AttributeError:
            pass

    async def __call__(self, request: Request):  # !!! retyrn type
        return await self.handler(request)


ParamsHandler = Callable[..., Awaitable[Any]]


def params_handler(handler: ParamsHandler) -> Handler:
    @functools.wraps(handler)
    async def wrapper(request):
        await handler(**request)
    return wrapper
