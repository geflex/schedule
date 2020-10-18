class Unloaded:
    def __init__(self, name, obj):
        self.name = name
        self.obj = obj

    def __getattr__(self, name):
        return Unloaded(name, self)

    def __call__(self, *args, **kwargs):
        return self.load()(*args, **kwargs)

    def load(self):
        obj, name = self.obj, self.name
        if isinstance(obj, Unloaded):
            return getattr(obj.load(), name)
        elif isinstance(obj, dict):
            return obj[name]

    def __repr__(self):
        return f'{self.__class__.__name__}({type(self.obj)}, {self.name})'
