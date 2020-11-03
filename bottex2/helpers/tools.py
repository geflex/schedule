import inspect
from types import FunctionType
from typing import Union, Type

from bottex2.views import View


Named = Union[Type[View], FunctionType]


def name(obj):
    if hasattr(obj, 'name'):
        return obj.name
    else:
        return obj.__name__


invisible_space = '\u200b'


def have_kwargs_parameter(function):
    """Checks whenever the function accepts **kwargs parameter"""
    sig = inspect.signature(function)
    return any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())
