from types import FunctionType
from typing import List, Union, Type

from bottex2.middlewares.users import state_cond
from bottex2.views import View


Named = Union[Type[View], FunctionType]


def name(obj):
    if hasattr(obj, 'name'):
        return obj.name
    else:
        return obj.__name__


def gen_state_conds(handlers: List[Named]):
    routes = {}
    for obj in handlers:
        if isinstance(obj, type) and issubclass(obj, View):
            handler = obj.handle
        else:
            handler = obj
        routes[state_cond(name(obj))] = handler
    return routes
