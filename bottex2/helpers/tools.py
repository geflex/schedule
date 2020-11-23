import inspect


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


invisible_space = '\u200b'


def have_kwargs_parameter(function):
    """Checks whenever the function accepts **kwargs parameter"""
    sig = inspect.signature(function)
    return any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())
