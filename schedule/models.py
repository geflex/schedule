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
session = Model.session


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
    group_name = Column(satypes.String, ForeignKey('groups.name'))
    subgroup = Column(subgroups)  # only for student

    group = relationship("Group")


class Group(Model):
    __tablename__ = 'groups'
    name = Column(satypes.String, unique=True, primary_key=True)

    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)

    def __repr__(self):
        return f'Group({self.name!r})'


class Teacher(Model):
    __tablename__ = 'teachers'

    id = Column(satypes.Integer, primary_key=True)
    last_name = Column(satypes.String)

    def __init__(self, last_name, **kwargs):
        super().__init__(last_name=last_name, **kwargs)

    def __repr__(self):
        return f'Teacher({self.last_name!r})'


lesson_teachers = Table('lesson_teachers', Model.metadata,
                        Column('lesson_id', satypes.Integer, ForeignKey('lessons.id')),
                        Column('teacher_id', satypes.Integer, ForeignKey('teachers.id'))
                        )


lesson_groups = Table('lesson_groups', Model.metadata,
                      Column('lesson_id', satypes.Integer, ForeignKey('lessons.id')),
                      Column('group_name', satypes.String, ForeignKey('groups.name'))
                      )


lesson_places = Table('lesson_places', Model.metadata,
                      Column('lesson_id', satypes.Integer, ForeignKey('lessons.id')),
                      Column('place_id', satypes.Integer, ForeignKey('places.id'))
                      )


class Building(Model):
    __tablename__ = 'buildings'
    name = Column(satypes.String, unique=True, primary_key=True)

    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)

    def __repr__(self):
        return f'Building({self.name!r})'


class Place(Model):
    __tablename__ = 'places'

    id = Column(satypes.Integer, primary_key=True)
    building_name = Column(satypes.String, ForeignKey('buildings.name'))
    building = relationship(Building)
    auditory = Column(satypes.String)

    def __init__(self, building, auditory, **kwargs):
        if building is None:
            building_name = None
        else:
            building_name = building.name
        super().__init__(building_name=building_name, auditory=auditory, **kwargs)

    def __repr__(self):
        return f'Group({self.building!r}, {self.auditory!r})'


class Lesson(Model):
    __tablename__ = 'lessons'

    id = Column(satypes.Integer, primary_key=True)
    weeknum = Column(satypes.Boolean)
    weekday = Column(satypes.Enum(Weekday))
    subgroup = Column(subgroups)
    time = Column(satypes.Time)
    name = Column(satypes.String)

    groups = relationship(Group, secondary=lesson_groups)
    teachers = relationship(Teacher, secondary=lesson_teachers)
    places = relationship(Place, secondary=lesson_places)
