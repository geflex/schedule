from enum import Enum, IntFlag
from typing import List

from sqlalchemy import Column, String, Integer
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


class Notifications:
    allowed: bool
    time: 'time'


class User(UserModel):
    locale = Column(String)
    notifications: Notifications
    rights: Rights

    ptype = Column(Integer)
    name = Column(String)  # for teacher
    group = Column(String)  # only for student
    subgroup = Column(String)  # only for student


class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True)
    group: str
    weeknum: int
    weekday: int
    subgroup: int
    time: str
    name: str
    teachers: List[str]
    building: str
    auditories: List[str]
