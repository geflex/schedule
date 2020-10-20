import re
from typing import Optional, MutableMapping, Callable, Union, Pattern, Iterator

from bottex2 import aiotools
from bottex2.handler import Handler, check_handler, HandlerError


class NoHandlerError(HandlerError):
    pass


Condition = Callable[..., bool]


class Router(Handler):
    def __init__(self):
        super().__init__()
        self.default = None  # type: Optional[Handler]
        self._handlers = {}  # type: MutableMapping[Condition, Handler]

    def __repr__(self):
        return f'{self.__class__.__name__}(default={self.default}, {self._handlers})'

    def set_default(self, handler: Handler) -> Handler:
        check_handler(handler)
        self.default = handler
        return handler

    def get(self, condition: Condition) -> 'Router':
        check_condition(condition)
        # noinspection PyTypeChecker
        return self._handlers.setdefault(condition, Router())

    def register(self, *conditions: Optional[Condition]):
        """It's too hard to explain correctly what this method does"""
        router = self
        for condition in conditions:
            router = router.get(condition)
        return router.set_default

    def find_handler(self, **params) -> Handler:
        """Searches and returns handler matching registered conditions."""
        handler = self.default
        for cond, h in self._handlers.items():
            if cond(**params):
                handler = h
                break
        if handler is None:
            raise NoHandlerError
        return handler

    async def __call__(self, **params):
        handler = self.find_handler(**params)
        await handler(**params)


def text_cond(s: str) -> Condition:
    def cond(text: str, **params) -> bool:
        return text.lower() == s.lower()
    return cond


def regexp_cond(exp: Union[str, Pattern]) -> Condition:
    exp = re.compile(exp)
    def cond(text: str, **params) -> bool:
        m = exp.match(text.lower(), re.I)
        return bool(m)
    return cond


def words_cond(*wds: str) -> Condition:
    def cond(text: str, **params) -> bool:
        return text.lower() in wds
    return cond


def any_cond(conditions: Iterator[Condition]) -> Condition:
    def cond(**params):
        return any(c(**params) for c in conditions)
    return cond


def check_condition(condition: Condition):
    if not callable(condition):
        raise TypeError('`Condition` must be callable')
    if not aiotools.have_kwargs_parameter(condition):
        raise ValueError('`Condition` must have a **kwargs parameter')
