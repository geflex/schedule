from typing import Optional, Callable, Awaitable, Dict, Any

from bottex2.handler import Handler, Request, TResponse

TCondition = Callable[[Request], bool]


class ConditionDict(dict, Dict[TCondition, Any]):
    def __init__(self,
                 mapping: Optional[Dict[TCondition, Any]] = None,
                 default: Optional[Handler] = None):
        super().__init__(mapping or {})
        self.default = default

    def get_value(self, request: Request) -> Any:
        """Searches and returns value matching conditions"""
        handler = self.default
        for cond, h in self.items():
            if cond(request):
                handler = h
                break
        if handler is None:
            raise KeyError
        return handler

    def __repr__(self):
        return f'{self.__class__.__name__}(default={self.default}, {super().__repr__()})'


class Router(ConditionDict, Dict[TCondition, Handler], Handler):
    def __init__(self,
                 routes: Optional[Dict[TCondition, Handler]] = None,
                 default: Optional[Handler] = None,
                 state_name: Optional[str] = None):
        super().__init__(routes, default)
        self.default_handler = default
        if state_name:
            self.state_name = state_name

    def __call__(self, request: Request) -> Awaitable[TResponse]:
        handler = self.get_value(request)
        return handler(request)
