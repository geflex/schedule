from enum import Enum, IntFlag

from sqlalchemy import Column, Table, ForeignKey, create_engine
from sqlalchemy import types as sqltypes
from sqlalchemy.orm import relationship

from bottex2.ext.i18n import I18nEnv
from bottex2.ext.rights import RightsUserMixin
from bottex2.ext.users import UserModel
from bottex2.sqlalchemy import Model
from . import configs

engine = create_engine(configs.db_url)
Model.set_engine(engine)
Model.create_tables()


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


class Rights(IntFlag):
    view = 1
    edit = 2
    notifying = 3


class Lang(Enum):
    ru = 'ru'
    en = 'en'
    be = 'be'


i18n = I18nEnv(Lang, default_lang=Lang.ru, domain='schedule')
subgroups = sqltypes.Enum('1', '2', name='subgroup')


class User(UserModel, i18n.UserMixin, RightsUserMixin):
    notifications_time = Column(sqltypes.Time, nullable=True)

    rights = Column(sqltypes.Enum(Rights))

    ptype = Column(sqltypes.Enum(PType))
    name = Column(sqltypes.String)  # for teacher
    group = Column(sqltypes.String)  # only for student
    subgroup = Column(subgroups)  # only for student


class Group(Model):
    __tablename__ = 'groups'

    id = Column(sqltypes.Integer, primary_key=True)
    name = Column(sqltypes.String)


class Teacher(Model):
    __tablename__ = 'teachers'

    id = Column(sqltypes.Integer, primary_key=True)
    last_name = Column(sqltypes.String)


lesson_teachers = Table('lesson_teachers', Model.metadata,
    Column('lesson_id', sqltypes.Integer, ForeignKey('lessons.id')),
    Column('teacher_id', sqltypes.Integer, ForeignKey('teachers.id'))
)


class Building(Model):
    __tablename__ = 'buildings'
    subgroup = Column(sqltypes.Enum('1', '2', name='subgroup'))  # only for student

    id = Column(sqltypes.Integer, primary_key=True)
    name = Column(sqltypes.String)


class Place(Model):
    __tablename__ = 'places'

    id = Column(sqltypes.Integer, primary_key=True)
    building_id = Column(sqltypes.Integer, ForeignKey('buildings.id'))
    auditory = Column(sqltypes.String)


class Lesson(Model):
    __tablename__ = 'lessons'

    id = Column(sqltypes.Integer, primary_key=True)
    weeknum = Column(sqltypes.Boolean)
    weekday = Column(sqltypes.Enum(Weekday))
    subgroup = Column(subgroups)
    time = Column(sqltypes.Time)
    name = Column(sqltypes.String)

    group_ids = Column(sqltypes.Integer, ForeignKey('groups.id'))
    teacher_ids = Column(sqltypes.Integer, ForeignKey('teachers.id'))
    place_ids = Column(sqltypes.Integer, ForeignKey('places.id'))

    groups = relationship(Group)
    teachers = relationship(Teacher, secondary=lesson_teachers)
    places = relationship(Place)
