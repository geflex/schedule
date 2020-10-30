from enum import Enum, IntFlag
from typing import List

from bottex2.databases.mongodb import MongoUser


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


class User(MongoUser):
    locale: str
    notifications: Notifications
    state: str
    view_args: dict
    rights: Rights

    ptype: PType
    name: str  # for teacher
    group: str  # only for student
    subgroup: str  # only for student


class Lesson:
    group: str
    weeknum: int
    weekday: int
    subgroup: int
    time: str
    name: str
    teachers: List[str]
    building: str
    auditories: List[str]
