import functools
from typing import Callable, Awaitable, Any

from bottex2.handler import Handler

ParamsHandler = Callable[..., Awaitable[Any]]


def params_handler(handler: ParamsHandler) -> Handler:
    @functools.wraps(handler)
    async def wrapper(request):
        await handler(**request)
    return wrapper
