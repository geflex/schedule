from collections import Callable
from typing import Any, Optional, List


def dummy(value):
    pass

noparser = dummy


class DictSchema:
    __attrs__: List

    def __init__(self, obj: dict):
        self.raw = obj

    def __init_subclass__(cls, **kwargs):
        cls.__attrs__ = []
        annotations = getattr(cls, '__annotations__', {})
        for name, attr in cls.__dict__.items():
            if isinstance(attr, Attr):
                if attr.name is None:
                    attr.name = name
                if not attr.parser:
                    attr.parser = annotations.get(attr.name, noparser)
                cls.__attrs__.append(attr)

    def init_all(self):
        for attr in self.__attrs__:
            getattr(self, attr.name)


class Attr:
    def __init__(self,
                 name=Optional[str],
                 parser: Callable[Any] = None,
                 is_optional=True):
        self.name = None
        self.parser = parser
        self.is_optional = is_optional

    def __get__(self, instance, owner):
        if instance is None:
            return self
        try:
            value = instance.raw[self.name]
        except KeyError:
            if self.is_optional:
                value = None
            else:
                raise
        value = self.parser(value)
        setattr(instance, self.name, value)
        return value


class Array:
    def __init__(self, parser):
        self._parser = parser

    def __call__(self, objects):
        return [self._parser(obj) for obj in objects]
