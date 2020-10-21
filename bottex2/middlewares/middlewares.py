from typing import Callable, TypeVar


Interface = TypeVar('Interface')
AbstractMiddleware = Callable[[Interface], Interface]


def check_middleware(middleware: AbstractMiddleware):
    if not callable(middleware):
        raise TypeError('middleware must be callable')
