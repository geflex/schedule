from typing import Optional, Callable, Awaitable, Dict

from bottex2.handler import Handler, Request, TResponse


class NoHandlerFoundError:
    pass


TCondition = Callable[[Request], bool]


class Router(dict, Dict[TCondition, Handler], Handler):
    def __init__(self,
                 routes: Optional[Dict[TCondition, Handler]] = None,
                 default: Optional[Handler] = None,
                 name: Optional[str] = None):
        super().__init__(routes or {})
        self.default_handler = default
        if name:
            self.state_name = name

    def find_handler(self, request: Request) -> Handler:
        """Searches and returns handler matching registered conditions"""
        handler = self.default_handler
        for cond, h in self.items():
            if cond(request):
                handler = h
                break
        if handler is None:
            raise NoHandlerFoundError
        return handler

    def __repr__(self):
        return f'{self.__class__.__name__}(default={self.default_handler}, {super().__repr__()})'

    def __call__(self, request: Request) -> Awaitable[TResponse]:
        handler = self.find_handler(request)
        return handler(request)
