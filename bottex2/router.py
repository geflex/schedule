import re
from typing import Optional, MutableMapping, Callable, Union, Pattern, Iterator

from bottex2.handler import Handler, check_handler, HandlerError, Request
from bottex2.helpers import tools
from bottex2.logging import logger


class NoHandlerError(HandlerError):
    pass


Condition = Callable[[Request], bool]


class Router(Handler):
    def __init__(self,
                 routes: MutableMapping[Condition, Handler] = None,
                 default: Optional[Handler] = None,
                 name: str = None):
        super().__init__()
        self.default = default
        self.routes = routes or {}
        if name:
            self.__name__ = name

    def set_default(self, handler: Handler) -> Handler:
        check_handler(handler)
        self.default = handler
        return handler

    def register(self, *conditions: Optional[Condition]):
        """Decorator to register handler for described conditions"""
        router = self
        for condition in conditions:
            router = router.routes[condition]
        return router.set_default

    def add_route(self, condition, handler):
        self.routes[condition] = handler

    def find_handler(self, request: Request) -> Handler:
        """Searches and returns handler matching registered conditions"""
        handler = self.default
        for cond, h in self.routes.items():
            if cond(request):
                handler = h
                break
        if handler is None:
            raise NoHandlerError
        return handler

    async def __call__(self, request: Request):
        handler = self.find_handler(request)
        await handler(request)

    def __repr__(self):
        return f'{self.__class__.__name__}(default={self.default}, {self.routes})'


def if_text(s: str) -> Condition:
    s = s.lower()
    def cond(request: Request) -> bool:
        return request.text.lower() == s.lower()
    return cond


def if_regexp(exp: Union[str, Pattern]) -> Condition:
    exp = re.compile(exp)
    def cond(request: Request) -> bool:
        m = exp.match(request.text)
        return bool(m)
    return cond


def if_text_in(*wds: str) -> Condition:
    wds = [w.lower() for w in wds]
    def cond(request: Request) -> bool:
        return request.text.lower() in wds
    return cond


def if_in(conditions: Iterator[Condition]) -> Condition:
    def cond(request: Request):
        return any(c(request) for c in conditions)
    return cond


def is_case_valid(condition: Condition):
    if not callable(condition):
        raise TypeError('`Condition` must be callable')
    if not tools.have_kwargs_parameter(condition):
        logger.warning('`Condition` must have a **kwargs parameter')
