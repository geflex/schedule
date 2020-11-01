from types import FunctionType
from typing import List, Union, Type

from bottex2.middlewares.users import state_cond
from bottex2.views import View


def gen_state_conds(handlers: List[Union[Type[View], FunctionType]]):
    routes = {}
    for handler in handlers:
        if isinstance(handler, type) and issubclass(handler, View):
            routes[state_cond(handler.name)] = handler.handle
            state, handler = handler.name, handler.handle
        else:
            state = handler.__name__
        routes[state_cond(state)] = handler
    return routes
