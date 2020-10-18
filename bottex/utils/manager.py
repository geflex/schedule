from collections import defaultdict


class NameManager(defaultdict):
    def __init__(self):
        super().__init__()

    def register(self, name=None):
        if name is None:
            def _reg(f):
                if hasattr(f, '__viewname__'):
                    self[f.__viewname__] = f
                else:
                    self[f.__name__] = f
        else:
            def _reg(f):
                self[name] = f

        def _register(func):
            _reg(func)
            return func
        return _register
