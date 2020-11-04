from enum import IntFlag

from sqlalchemy import Column, types as sqltypes


class Rights(IntFlag):
    view = 1
    edit = 2
    notifying = 3


class RightsMixin:
    rights = Column(sqltypes.Enum(Rights))
