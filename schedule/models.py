from enum import Enum, IntFlag

from sqlalchemy import Column, Table, ForeignKey, create_engine
from sqlalchemy import types as satypes
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
subgroups = satypes.Enum('1', '2', name='subgroup')


class User(UserModel, i18n.UserMixin, RightsUserMixin):
    notifications_time = Column(satypes.Time, nullable=True)

    rights = Column(satypes.Enum(Rights))

    ptype = Column(satypes.Enum(PType))
    name = Column(satypes.String)  # for teacher
    group_id = Column(satypes.Integer, ForeignKey('groups.id'))
    subgroup = Column(subgroups)  # only for student

    group = relationship("Group")


class Group(Model):
    __tablename__ = 'groups'

    id = Column(satypes.Integer, primary_key=True)
    name = Column(satypes.String)


class Teacher(Model):
    __tablename__ = 'teachers'

    id = Column(satypes.Integer, primary_key=True)
    last_name = Column(satypes.String)


lesson_teachers = Table('lesson_teachers', Model.metadata,
                        Column('lesson_id', satypes.Integer, ForeignKey('lessons.id')),
                        Column('teacher_id', satypes.Integer, ForeignKey('teachers.id'))
                        )


class Building(Model):
    __tablename__ = 'buildings'
    id = Column(satypes.Integer, primary_key=True)
    name = Column(satypes.String)


class Place(Model):
    __tablename__ = 'places'

    id = Column(satypes.Integer, primary_key=True)
    building_id = Column(satypes.Integer, ForeignKey('buildings.id'))
    building = relationship(Building)
    auditory = Column(satypes.String)


class Lesson(Model):
    __tablename__ = 'lessons'

    id = Column(satypes.Integer, primary_key=True)
    weeknum = Column(satypes.Boolean)
    weekday = Column(satypes.Enum(Weekday))
    subgroup = Column(subgroups)
    time = Column(satypes.Time)
    name = Column(satypes.String)

    group_ids = Column(satypes.Integer, ForeignKey('groups.id'))
    teacher_ids = Column(satypes.Integer, ForeignKey('teachers.id'))
    place_ids = Column(satypes.Integer, ForeignKey('places.id'))

    groups = relationship(Group)
    teachers = relationship(Teacher, secondary=lesson_teachers)
    places = relationship(Place)
