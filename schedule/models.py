from enum import IntFlag

from sqlalchemy import Column, Table, ForeignKey, create_engine
from sqlalchemy import types as satypes
from sqlalchemy.orm import relationship

from bottex2.ext.i18n import I18n, BaseLang
from bottex2.ext.rights import Rights as RightsEnv
from bottex2.ext.users import Users
from bottex2.helpers import tables
from bottex2.multiplatform import MultiplatformUserMixin
from bottex2.sqlalchemy import SQLAlchemy
from bottex2.states import StateUserMixin
from . import configs


def _(s): return s
_c = _
engine = create_engine(configs.db_url)
db = SQLAlchemy(engine)


class Department(tables.Table):
    abbr = tables.Column(primary=True)
    name = tables.Column()

    __values__ = (
        ('АТФ', 'Автотракторный Факультет'),
        ('ФГДЕ', 'Факультет горного дела и инженерной экологии'),
        ('МСФ', 'Машиностроительный Факультет'),
        ('МТФ', 'Механикотехнологический Факультет'),
        ('ФММП', 'Факультет Маркетинга, менеджмента и предпринимательства'),
        ('ЭФ', 'Энергитический Факультет'),
        ('ФИТР', 'Факультет информационных технологий и робототехники'),
        ('ФТУГ', 'Факультет технологий управления и гуманитаризации'),
        ('ИПФ', 'Инженерно-педагогический факультет'),
        ('ФЭС', 'Факультет энергитического строительства'),
        ('АФ', 'Фрхитектурный Факультет'),
        ('СФ', 'Строительный факультет'),
        ('ПСФ', 'Приборостроительный факультет'),
        ('ФТК', 'Факультет транспортных коммуникаций'),
        ('ВТФ', 'Военно-технический факультет'),
        ('СТФ', 'Спортивно-технический факультет'),
    )


class PType(tables.Table):
    db_val = tables.Column(primary=True)
    name = tables.Column()
    num = tables.Column()

    __values__ = (
        ('student', _c('студент'), 0),
        ('teacher', _c('преподаватель'), 1),
    )


class Lang(BaseLang):
    __values__ = (
        ('ru', 'Русский'),
        ('en', 'English'),
        ('be', 'Беларусская'),
    )

i18n = I18n(Lang, default_lang=Lang['ru'],
            lcdir='schedule/locales',
            domain_name='schedule')


class RightsEnum(IntFlag):
    view = 1
    edit = 2
    notifying = 3

rights = RightsEnv(RightsEnum)


class Weekday(tables.Table):
    num = tables.Column(primary=True)
    short_name = tables.Column()
    full_name = tables.Column()

    __values__ = (
        (0, _c('пн'), _c('понедельник')),
        (1, _c('вт'), _c('вторник')),
        (2, _c('ср'), _c('среда')),
        (3, _c('чт'), _c('четверг')),
        (4, _c('пт'), _c('пятница')),
        (5, _c('сб'), _c('суббота')),
        (6, _c('вс'), _c('воскресенье')),
    )


class Subgroup(tables.Table):
    num = tables.Column(primary=True)
    name = tables.Column()
    __values__ = (
        ('1', _c('первая')),
        ('2', _c('вторая')),
    )


class User(db.Model, MultiplatformUserMixin, StateUserMixin, i18n.UserMixin, rights.UserMixin):
    __tablename__ = 'users'

    notifications_time = Column(satypes.Time, nullable=True)

    ptype = Column(satypes.Enum(PType))
    name = Column(satypes.String)  # for teacher
    subgroup = Column(satypes.Enum(Subgroup))  # only for student
    group_name = Column(satypes.String, ForeignKey('groups.name'))

    group = relationship("Group")


users = Users(User)


class Group(db.Model):
    __tablename__ = 'groups'
    name = Column(satypes.String, unique=True, primary_key=True)

    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)

    def __repr__(self):
        return f'Group({self.name!r})'


class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = Column(satypes.Integer, primary_key=True)
    last_name = Column(satypes.String)

    def __init__(self, last_name, **kwargs):
        super().__init__(last_name=last_name, **kwargs)

    def __repr__(self):
        return f'Teacher({self.last_name!r})'


lesson_teachers = Table('lesson_teachers', db.metadata,
                        Column('lesson_id', satypes.Integer, ForeignKey('lessons.id')),
                        Column('teacher_id', satypes.Integer, ForeignKey('teachers.id'))
                        )


lesson_groups = Table('lesson_groups', db.metadata,
                      Column('lesson_id', satypes.Integer, ForeignKey('lessons.id')),
                      Column('group_name', satypes.String, ForeignKey('groups.name'))
                      )


lesson_places = Table('lesson_places', db.metadata,
                      Column('lesson_id', satypes.Integer, ForeignKey('lessons.id')),
                      Column('place_id', satypes.Integer, ForeignKey('places.id'))
                      )


class Building(db.Model):
    __tablename__ = 'buildings'
    name = Column(satypes.String, unique=True, primary_key=True)

    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)

    def __repr__(self):
        return f'Building({self.name!r})'


class Place(db.Model):
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


class Lesson(db.Model):
    __tablename__ = 'lessons'

    id = Column(satypes.Integer, primary_key=True)
    second_weeknum = Column(satypes.Boolean)
    weekday_num = Column(satypes.Integer)
    subgroup = Column(satypes.Enum(Subgroup))
    time = Column(satypes.Time)
    name = Column(satypes.String)

    groups = relationship(Group, secondary=lesson_groups)
    teachers = relationship(Teacher, secondary=lesson_teachers)
    places = relationship(Place, secondary=lesson_places)


db.create_all()
