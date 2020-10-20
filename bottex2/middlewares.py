from __future__ import annotations

from abc import ABC
from typing import List, Callable, TypeVar
import functools

Interface = TypeVar('Interface')
AbstractMiddleware = Callable[[Interface], Interface]


def check_middleware(middleware: AbstractMiddleware):
    if not callable(middleware):
        raise TypeError('middleware must be callable')


class Middlewarable(ABC):
    """
    This class provides interface and functionality for
    classes that contain and use `AbstractMiddleware` interface
    """

    def __init__(self):
        self.middlewares = []  # type: List[AbstractMiddleware]

    def add_middleware(self, middleware: AbstractMiddleware):
        """Adds middleware to a container"""
        check_middleware(middleware)
        self.middlewares.append(middleware)

    def _wrap_into_middlewares(self, handler: Interface) -> Interface:
        return functools.reduce(lambda h, md: md(h), self.middlewares, handler)
