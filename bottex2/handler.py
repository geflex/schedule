import inspect
from typing import Awaitable, TypedDict, Any, Callable

from bottex2 import tools
from bottex2.chat import Chat


class Params(TypedDict):
    text: str
    chat: Chat
    raw: Any


Handler = Callable[..., Awaitable]

# class Handler(Protocol):
#     async def __call__(self,
#                        text: str,
#                        chat: Chat,
#                        raw: Dict[str, Any],
#                        **params: Any) -> Awaitable:
#         pass


class HandlerError(Exception):
    pass


def check_handler(handler: Handler):
    if not callable(handler):
        raise TypeError('`Handler` must be callable')
    sig = inspect.signature(handler)
    if not tools.have_kwargs_parameter(handler):
        raise ValueError('`Handler` must have a **kwargs parameter')
