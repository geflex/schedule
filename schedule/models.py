import logging
from enum import Enum, IntFlag

from mongoengine import *


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


connect(db='schedule_test')


class Notifications(DynamicEmbeddedDocument):
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

    logger = logging.getLogger('_user_class')

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
