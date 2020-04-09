class DictSchema:
    __attrs__ = []

    def __init__(self, obj: dict):
        self.raw = obj

    def __init_subclass__(cls, **kwargs):
        cls.__attrs__ = attrs = []
        annotations = getattr(cls, '__annotations__', {})
        for name, attr in cls.__dict__.items():
            if isinstance(attr, Attr):
                if not attr.name:
                    attr.name = name
                if not attr.parser:
                    attr.parser = annotations.get(attr.name, noparser)
                attrs.append(attr)

    def init_all(self):
        for attr in self.__attrs__:
            getattr(self, attr.name)


def noparser(obj):
    return obj


class Attr:
    def __init__(self, parser=None, optional=True):
        self.name = None
        self.parser = parser
        self.optional = optional

    def __get__(self, instance, owner):
        if instance is None:
            return self
        try:
            value = instance.raw[self.name]
        except KeyError:
            if self.optional:
                value = None
            else:
                raise
        value = self.parser(value)
        setattr(instance, self.name, value)
        return value


def array(parser):
    def _create_array(objects):
        return [parser(obj) for obj in objects]
    return _create_array
