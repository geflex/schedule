from enum import Enum, IntFlag, auto

from mongoengine import *

import bottex
from bottex.models.mongodriver import EnumField, TimeField
from bottex.models import UserModel, NotificationsModel
from bottex.utils.enums import StrEnum


class Lang(StrEnum):
    ru = 'ru'
    en = 'en'
    be = 'be'


class Rights(IntFlag):
    view = auto()
    edit = auto()
    notifying = auto()


class Department(StrEnum):
    atf = auto()
    fgde = auto()
    msf = auto()
    mtf = auto()
    fmmp = auto()
    ef = auto()
    fitr = auto()
    ftug = auto()
    ipf = auto()
    fes = auto()
    af = auto()
    sf = auto()
    psf = auto()
    ftk = auto()
    vtf = auto()
    mido = auto()


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


connect(db='schedule_test')


class Notifications(NotificationsModel, DynamicEmbeddedDocument):
    allowed = BooleanField()
    time = TimeField()


class User(UserModel, DynamicDocument):
    meta = {'collection': 'users'}

    site = StringField()
    uid = StringField()
    locale = EnumField(Lang, default=Lang.ru)
    notifications = EmbeddedDocumentField(
        Notifications,
        default=Notifications(allowed=False, time=None)
    )
    last_view = StringField(default='')
    view_args = DictField()
    rights = IntField(default=Rights.view)

    ptype = EnumField(PType, default=PType.student)
    name = StringField()  # for teacher
    group = StringField()  # only for student
    subgroup = StringField()  # only for student

    def __repr__(self):
        return f'{self.__class__.__name__}({self.site!r}, {self.uid})'

    logger = bottex.utils.logging.get_logger('_user_class')

    @classmethod
    def get_or_add(cls, site, uid):
        user = cls.objects(site=site, uid=uid).first()
        if user is None:
            user = cls(site=site, uid=uid)
            user.save()
            cls.logger.debug(f'new user registered: {user}')
        return user


class Lesson(DynamicDocument):
    meta = {'collection': 'lessons'}

    group = StringField()
    weeknum = IntField()
    weekday = IntField()
    subgroup = IntField()
    time = StringField()
    name = StringField()
    teachers = ListField(StringField())
    building = StringField()
    auditories = ListField(StringField())


class Groups(DynamicDocument):
    meta = {'collection': 'groups'}

    name = StringField()
    department = EnumField(Department)
    course = IntField()
    speciality = StringField()


class Teachers(DynamicDocument):
    meta = {'collection': 'teachers'}

    firstname = StringField()
    lastname = StringField()
    middlename = StringField()
    department = StringField()
