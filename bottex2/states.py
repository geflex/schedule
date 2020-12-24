from typing import Iterable, Dict

from sqlalchemy import Column, String

from bottex2.handler import Request, Handler
from bottex2.router import TCondition


def state_name(obj):
    if hasattr(obj, 'state_name'):
        return obj.state_name
    else:
        return obj.__name__


def state_handler(obj):
    if isinstance(obj, type) and hasattr(obj, 'handle'):
        return obj.handle
    else:
        return obj


class StateUserMixin:
    state = Column(String)


def state_cond(st: str) -> TCondition:
    def cond(request: Request) -> bool:
        return request.user.state == st
    return cond


def gen_state_cases(handlers: Iterable) -> Dict[TCondition, Handler]:
    routes = {}
    for obj in handlers:
        name, handler = state_name(obj), state_handler(obj)
        routes[state_cond(name)] = handler
    return routes
