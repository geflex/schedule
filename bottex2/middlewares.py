from __future__ import annotations

from abc import ABC
from typing import List, Callable, TypeVar


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

    def add_handler_middleware(self, middleware: AbstractMiddleware):
        """Adds middleware to an owner"""
        check_middleware(middleware)
        self.middlewares.append(middleware)
