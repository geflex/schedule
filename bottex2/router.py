from typing import Optional, MutableMapping, Callable, Awaitable

from bottex2.handler import Handler, Request, TResponse


class NoHandlerFoundError:
    pass


TCondition = Callable[[Request], bool]


class Router(Handler):
    def __init__(self,
                 routes: MutableMapping[TCondition, Handler] = None,
                 default: Optional[Handler] = None,
                 name: str = None):
        self.default_handler = default
        self._routes = routes or {}
        if name:
            self.state_name = name

    @property
    def routes(self):
        return self._routes

    def __repr__(self):
        return f'{self.__class__.__name__}(default={self.default_handler}, {self._routes})'

    def __getitem__(self, condition: TCondition):
        return self._routes[condition]

    def __setitem___(self, condition: TCondition, handler: Handler):
        self._routes[condition] = handler

    def __delitem__(self, condition):
        del self._routes[condition]

    def __len__(self):
        return len(self._routes)

    def find_handler(self, request: Request) -> Handler:
        """Searches and returns handler matching registered conditions"""
        handler = self.default_handler
        for cond, h in self._routes.items():
            if cond(request):
                handler = h
                break
        if handler is None:
            raise NoHandlerFoundError
        return handler

    def __call__(self, request: Request) -> Awaitable[TResponse]:
        handler = self.find_handler(request)
        return handler(request)
