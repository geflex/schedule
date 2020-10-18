from __future__ import annotations

from abc import ABC
from typing import List, Callable
import functools

from bottex2.handler import Handler


Middleware = Callable[[Handler], Handler]


def check_middleware(middleware: Middleware):
    if not callable(middleware):
        raise TypeError('middleware must be callable')


class MiddlewareContainer(ABC):
    """
    This class provides interface and functionality for
    classes that contain and use `Middleware` interface
    """

    def __init__(self):
        self.middlewares = []  # type: List[Middleware]

    def add_middleware(self, middleware: Middleware):
        """Adds middleware to a container"""
        check_middleware(middleware)
        self.middlewares.append(middleware)

    def _wrap_into_middlewares(self, handler: Handler) -> Handler:
        return functools.reduce(lambda h, md: md(h), self.middlewares, handler)
