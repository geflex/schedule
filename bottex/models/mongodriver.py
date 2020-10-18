from collections import namedtuple
import datetime

from mongoengine.fields import BaseField, DateTimeField


class Mapper:
    def fields(self):
        # noinspection PyUnresolvedReferences
        return self._cls._fields

    def __init__(self, fields, data=()):
        if isinstance(fields, str):
            fields = fields.split(' ')
        self._cls = namedtuple('mapper', fields)
        self.data = {}
        self.extend(data)

    def __call__(self, *args, **kwargs):
        return self._cls(*args, **kwargs)

    def extend(self, data):
        for item in data:
            self.append(item)

    def append(self, item):
        self.data[item[0]] = (self._cls(*item))

    def __iter__(self):
        yield from self.data

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return f'Mapper(data={self.data})'

    def get(self, **kwargs):
        assert len(kwargs) == 1
        n, v = next(iter(kwargs.items()))
        return next(item for item in self.data.values() if getattr(item, n) == v)

    def get_by_index(self, field_ind, val):
        return next(item for item in self.data.values() if item[field_ind] == val)

    def __getitem__(self, item):
        return self.data[item]

    def __getattr__(self, item):
        return self[item]


class EnumField(BaseField):
    def __init__(self, enum, **kwargs):
        self.enum = enum
        super().__init__(choices=enum, **kwargs)

    def __get_val(self, value):
        return value.value if hasattr(value, 'value') else value

    def to_python(self, value):
        v = super().to_python(value)
        return self.enum(v)

    def to_mongo(self, value):
        return self.__get_val(value)

    def prepare_query_value(self, op, value):
        return super().prepare_query_value(op, value)

    def validate(self, value, clean=True):
        return super().validate(value.value)

    def _validate(self, value, **kwargs):
        return super()._validate(self.enum(value.value), **kwargs)


class LanguageField(BaseField):
    pass


class TimeField(DateTimeField):
    def to_mongo(self, value):
        if isinstance(value, datetime.time):
            value = datetime.datetime(1, 1, 1, value.hour, value.minute)
        value = super().to_mongo(value)
        return value

    def to_python(self, value):
        if isinstance(value, datetime.datetime):
            value = datetime.time(value.hour, value.minute)
        value = super().to_python(value)
        return value
