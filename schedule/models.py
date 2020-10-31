from enum import Enum, IntFlag
from typing import List

from sqlalchemy import Column
from sqlalchemy import types as sqltypes
from sqlalchemy.orm import relationship

from bottex2.middlewares.users import UserModel
from bottex2.sqlalchemy import Base


class Lang(Enum):
    ru = 'ru'
    en = 'en'
    be = 'be'


class Rights(IntFlag):
    view = 1
    edit = 2
    notifying = 3


class Department(Enum):
    atf = 'atf'
    fgde = 'fgde'
    msf = 'msf'
    mtf = 'mtf'
    fmmp = 'fmmp'
    ef = 'ef'
    fitr = 'fitr'
    ftug = 'ftug'
    ipf = 'ipf'
    fes = 'fes'
    af = 'af'
    sf = 'sf'
    psf = 'psf'
    ftk = 'ftk'
    vtf = 'vtf'
    mido = 'mido'


class Weekday(Enum):
    mon = 0
    tue = 1
    wed = 2
    thu = 3
    fri = 4
    sat = 5
    sun = 6


class PType(Enum):
    student = 0
    teacher = 1


class User(UserModel):
    notifications_time = Column(sqltypes.Time, nullable=True)

    locale = Column(sqltypes.Enum(Lang), default=Lang.ru)
    rights = Column(sqltypes.Enum(Rights))

    ptype = Column(sqltypes.Enum(PType))
    name = Column(sqltypes.String)  # for teacher
    group = Column(sqltypes.String)  # only for student
    subgroup = Column(sqltypes.String)  # only for student


class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(sqltypes.Integer, primary_key=True)
    groups: str
    weeknum: int
    weekday = Column(sqltypes.Enum(Weekday))
    subgroup = Column(sqltypes.Integer)
    time = Column(sqltypes.Time)
    name = Column(sqltypes.String)
    teachers: List[str]
    building = Column(sqltypes.String)
    auditories: List[str]
