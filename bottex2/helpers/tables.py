from __future__ import annotations

from copy import copy
from typing import Iterable, List, Any, Dict


class Item:
    _column_names: List[str]
    _primary_index: int

    def __init__(self, values: Iterable):
        self._values = tuple(values)

        self.primary_value = self._values[self._primary_index]
        for n, v in zip(self._column_names, values):
            setattr(self, n, v)

    @property
    def values(self):
        return self._values

    def __iter__(self):
        return iter(self._values)


class Column:
    def __init__(self, *, primary=False):
        self._is_primary = primary
        self._index = None
        self._cls = None

    @property
    def is_primary(self):
        return self._is_primary

    @property
    def index(self):
        return self._index

    def __getitem__(self, value) -> TableMeta:
        for item in self._cls.objects:
            if item.values[self._index] == value:
                return item
        raise KeyError

    def all(self) -> List[Any]:
        return [row[self._index] for row in self._cls.__values__]

    def __iter__(self):
        return iter(self.all())

    def __get__(self, instance: TableMeta, owner):
        if instance is None:
            return self
        return list(instance.values)[self._index]


class TableMeta(type):
    def __new__(mcs, name: str, bases: tuple, args: dict):
        # initializing class
        cls = super().__new__(mcs, name, bases, args)

        # configuring column objects
        if getattr(cls, '_columns', None) is None:
            cls._column_names = []
            cls._columns = []
        else:
            cls._column_names = copy(cls._column_names)
            cls._columns = copy(cls._columns)
        cls._primary_index = 0
        for n, v in args.items():
            if isinstance(v, Column):
                i = v._index = len(cls._columns)
                cls._column_names.append(n)
                cls._columns.append(v)
                if v.is_primary:
                    cls._primary_index = i

        for col in cls._columns:
            col._cls = cls

        # creating class objects
        values = args.get('__values__', [])
        cls._objects = [cls(vals) for vals in values]
        return cls

    @property
    def objects(cls):
        return cls._objects

    def __iter__(cls):
        return iter(cls._objects)

    def __len__(cls):
        return len(cls._objects)

    def __getitem__(cls, value):
        return cls.primary_column[value]

    @property
    def columns(cls) -> List[Column]:
        return cls._columns

    @property
    def primary_column(cls) -> Column:
        return cls.columns[cls._primary_index]

    @property
    def __members__(cls) -> Dict[str, TableMeta]:
        return dict(zip(cls.primary_column.all(), cls.objects))


class Table(Item, metaclass=TableMeta):
    __values__: Iterable[Iterable]
