from abc import abstractmethod, ABC
from functools import cached_property
from typing import List, Type

import sqlalchemy as sa

from bottex2.ext.users import gen_state_cases
from bottex2.handler import Request, Response, Handler
from bottex2.helpers.tools import state_name
from bottex2.router import Router
from bottex2.views import View, Command
from . import dateutils
from . import inputs
from . import models as m
from .dateutils import Date
from .models import i18n, Lang, Weekday, Subgroup, PType

_ = i18n.gettext
_c = i18n.rgettext


def group_str(group):
    return group.name if group else ''


def ptype_cond(ptype: PType):
    def cond(r):
        return r.user.ptype is ptype
    return cond

is_student = ptype_cond(PType['student'])
is_teacher = ptype_cond(PType['teacher'])


class Settings(View):
    state_name = 'settings'
    
    @cached_property
    def commands(self):
        commands = []
        def add(text, cb):
            commands.append([Command(text, cb)])

        add(_c('Изменить язык'), SettingsLanguageInput.switch)
        if self.r.user.ptype is PType['teacher']:
            add(_c('Режим студента'), self.become_student)
            add(_c('Изменить имя'), SettingsNameInput.switch)
        else:
            add(_c('Режим преподавателя'), self.become_teacher)
            add(_c('Изменить группу'), SettingsGroupInput.switch)
            add(_c('Изменить подгруппу'), SettingsSubgroupInput.switch)
        add(_c('Назад'), Schedule.switch)
        return commands

    async def become_student(self, r: Request):
        if not r.user.group:
            return await RequiredGroupInput.switch(r)
        if not r.user.subgroup:
            return await RequiredSubGroupInput.switch(r)
        else:
            return await save_student(r)

    async def become_teacher(self, r: Request):
        if not r.user.name:
            return await RequiredNameInput.switch(r)
        else:
            return await save_teacher(r)

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        return Response(_('Настройки'), cls(r).keyboard)


class BaseSettingsInput(View):
    @property
    def commands(self):
        return [[Command(_c('Отмена'), Settings.switch)]]


class SettingsLanguageInput(inputs.BaseLanguageInput, BaseSettingsInput):
    state_name = 'settings_lang'

    @cached_property
    def commands(self):
        commands = super().commands
        commands2 = super(inputs.BaseLanguageInput, self).commands
        return commands + commands2

    def get_lang_setter(self, lang: Lang):
        super_setter = super().get_lang_setter(lang)
        async def setter(r: Request):
            old = r.user.locale
            await super_setter(r)
            await r.user.update(state=state_name(Settings))
            return Response(
                _('Язык изменен с {} на {}').format(old.name, lang.name),
                Settings(r).keyboard
            )
        return setter

    @classmethod
    async def switch(cls, r: Request):
        kb = cls(r).keyboard
        current = r.user.locale  # type: Lang
        await super().switch(r)
        return [Response(_('Текущий язык: {}').format(current.name), kb),
                Response(_('Выбери новый язык'), kb)]


class SettingsGroupInput(inputs.BaseGroupInput, BaseSettingsInput):
    state_name = 'settings_group'

    @property
    def commands(self) -> List[List[Command]]:
        commands = super().commands
        commands2 = super(inputs.BaseGroupInput, self).commands
        return commands + commands2

    async def set_group(self, r: Request):
        old = r.user.group
        await super().set_group(r)
        await r.user.update(state=state_name(Settings))
        return Response(
            _('Группа изменена с {} на {}').format(group_str(old), group_str(r.user.group)),
            Settings(r).keyboard
        )

    @classmethod
    async def switch(cls, r: Request):
        kb = cls(r).keyboard
        await super().switch(r)
        return [Response(_('Текущая группа: {}').format(group_str(r.user.group)), kb),
                Response(_('Введи номер группы'), kb)]


class SettingsNameInput(inputs.BaseNameInput, BaseSettingsInput):
    state_name = 'settings_name'

    @cached_property
    def commands(self) -> List[List[Command]]:
        commands = super().commands
        commands2 = super(inputs.BaseNameInput, self).commands
        return commands + commands2

    async def set_name(self, r: Request):
        old = r.user.name
        await super().set_name(r)
        await r.user.update(state=state_name(Settings))
        return Response(_('Имя изменено с {} на {}').format(old, r.text),
                        Settings(r).keyboard)

    @classmethod
    async def switch(cls, r: Request):
        kb = cls(r).keyboard
        await super().switch(r)
        return [Response(_('Текущее имя: {}').format(r.user.name), kb),
                Response(_('Введи новое имя'), kb)]


class SettingsSubgroupInput(inputs.BaseSubgroupInput, BaseSettingsInput):
    state_name = 'settings_subgroup'

    @cached_property
    def commands(self):
        commands = super().commands
        commands2 = super(inputs.BaseSubgroupInput, self).commands
        return commands + commands2

    def get_subgroup_setter(self, subgroup: Subgroup):
        super_setter = super().get_subgroup_setter(subgroup)
        async def setter(r: Request):
            old = r.user.subgroup
            await super_setter(r)
            await r.user.update(state=state_name(Settings))
            return Response(
                _('Подгруппа изменена с {} на {}').format(old.name, subgroup.name),
                Settings(r).keyboard
            )
        return setter

    @classmethod
    async def switch(cls, r: Request):
        kb = cls(r).keyboard
        await super().switch(r)
        return [Response(_('Текущая подгруппа: {}').format(r.user.subgroup.name), kb),
                Response(_('Введи номер подгруппы'), kb)]


class BasePTypeRequiredInput(BaseSettingsInput):
    @property
    def commands(self) -> List[List[Command]]:
        return [[Command(_c('Отмена'), self.cancel)]]

    async def cancel(self, r: Request):
        return await Settings.switch(r)


class RequiredGroupInput(inputs.BaseGroupInput, BasePTypeRequiredInput):
    state_name = 'group_after_switching_ptype'

    @cached_property
    def commands(self):
        commands = super().commands
        commands2 = super(inputs.BaseGroupInput, self).commands
        return commands + commands2

    async def set_group(self, r: Request):
        result = await super().set_group(r)
        if not r.user.subgroup:
            return await RequiredSubGroupInput.switch(r)
        return await save_student(r)

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        return Response(_('Введи номер группы'), cls(r).keyboard)


class RequiredSubGroupInput(inputs.BaseSubgroupInput, BasePTypeRequiredInput):
    state_name = 'subgroup_after_switching_ptype'

    @cached_property
    def commands(self) -> List[List[Command]]:
        choises = super().commands
        commands = super(inputs.BaseSubgroupInput, self).commands
        return choises + commands

    def get_subgroup_setter(self, subgroup: Subgroup):
        super_setter = super().get_subgroup_setter(subgroup)
        async def setter(r: Request):
            await super_setter(r)
            return await save_student(r)
        return setter

    async def cancel(self, r: Request):
        await r.user.update(ptype=PType['teacher'])
        return await Settings.switch(r)

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        return Response(_('Выбери подгруппу'), cls(r).keyboard)


class RequiredNameInput(inputs.BaseNameInput, BasePTypeRequiredInput):
    state_name = 'name_after_switching_ptype'

    @cached_property
    def commands(self):
        commands = super().commands
        commands2 = super(inputs.BaseNameInput, self).commands
        return commands + commands2

    async def set_name(self, r: Request):
        await super().set_name(r)
        return await save_teacher(r)

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        return Response(_('Введи имя'), cls(r).keyboard)


async def save_teacher(r: Request):
    await r.user.update(state=state_name(Settings), ptype=PType['teacher'])
    return Response(_('Включен режим преподавателя'), Settings(r).keyboard)


async def save_student(r: Request):
    await r.user.update(state=state_name(Settings), ptype=PType['student'])
    return Response(_('Включен режим студента'), Settings(r).keyboard)


class LessonFormatter(ABC):
    @staticmethod
    def datefmt(date: Date):
        dt = date.strftime('%d.%m.%Y')
        weekday = Weekday.num[date.weekday()]
        return f'{dt}, {weekday.full_name.capitalize()}'

    def __init__(self, lesson: m.Lesson):
        self.lesson = lesson

    def auditories(self):
        return ', '.join(a.auditory for a in self.lesson.places)

    def time(self):
        t = self.lesson.time
        return t.strftime("%H:%M") if t else '--:--'

    def group(self):
        return ', '.join(g.name for g in self.lesson.groups)

    def subgroup(self):
        return self.lesson.subgroup

    def name(self):
        return self.lesson.name

    def building(self):
        if self.lesson.places:
            building = self.lesson.places[0].building
            if building is not None:
                return building.name
        return '(?)'

    def auditory(self):
        return ''.join(a.auditory for a in self.lesson.places) or '(?)'

    def teacher(self):
        return ', '.join(t.last_name for t in self.lesson.teachers)

    @abstractmethod
    def __str__(self):
        pass


class TeacherFormatter(LessonFormatter):
    def __str__(self):
        return f'{self.time()} {self.name()} к.{self.building()}, а.{self.auditory()}, {self.group()} ({self.subgroup()})'


class StudentFormatter(LessonFormatter):
    def __str__(self):
        return f'{self.time()} {self.name()} к.{self.building()}, а.{self.auditory()}, {self.teacher()}'


class Schedule(View, ABC):
    formatter_cls: Type[LessonFormatter]
    state_name = 'schedule'

    @property
    def commands(self):
        return [
            [Command(_c('Сегодня'), self.today), Command(_c('Завтра'), self.tomorrow)],
            [Command(_c(wd.short_name.capitalize()), self.weekday(wd)) for wd in list(Weekday)],
            [Command(_c('Настройки'), Settings.switch)],
        ]

    async def default(self, r: Request):
        return Response(_('Непонятная команда'))

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        return Response(_('Главное меню'), cls(r).keyboard)

    def _query_conditions(self, date):
        # noinspection PyComparisonWithNone
        week_cond = sa.or_(m.Lesson.second_weeknum == dateutils.is_second_weeknum(date),
                           m.Lesson.second_weeknum == None)
        weekday_cond = (m.Lesson.weekday_num == date.weekday())
        return week_cond, weekday_cond

    async def _schedule(self, date: Date, r: Request):
        pass

    @classmethod
    async def today(cls, r: Request):
        date = Date.today()
        return cls(r)._schedule(date, r)

    @classmethod
    async def tomorrow(cls, r: Request):
        date = Date.tomorrow()
        return cls(r)._schedule(date, r)

    @classmethod
    def weekday(cls, weekday: Weekday) -> Handler:
        delta = Date.today().weekday() - weekday.num
        date = Date.today().days_decr(delta)
        async def handler(r: Request):
            return cls(r)._schedule(date, r)
        return handler

    def no_lessons_response(self) -> Response:
        return Response(_('Занятий нет)'))


class TeacherSchedule(Schedule):
    formatter_cls = TeacherFormatter

    def _schedule(self, date: Date, r: Request):
        user = r.user

        query = m.Lesson.query.filter(
            m.Lesson.teachers.any(last_name=user.name),
            *self._query_conditions(date),
        )
        query = query.all()
        if query:
            message_str = _('Преподаватель {}\n'
                            '{}').format(user.name, self.formatter_cls.datefmt(date))
            lessons_str = '\n'.join(str(self.formatter_cls(l)) for l in query)
            return [Response(message_str),
                    Response(lessons_str)]
        return self.no_lessons_response()


class StudentSchedule(Schedule):
    formatter_cls = StudentFormatter

    def _schedule(self, date: Date, r: Request):
        user = r.user

        # noinspection PyComparisonWithNone
        query = m.Lesson.query.filter(
            m.Lesson.groups.any(name=user.group.name),
            sa.or_(
                m.Lesson.subgroup == user.subgroup,
                m.Lesson.subgroup == None,
            ),
            *self._query_conditions(date),
        )
        query = query.all()
        if query:
            message_str = _('Группа {}\n'
                            '{} подгруппа\n'
                            '{}').format(user.group.name,
                                         user.subgroup.name,
                                         self.formatter_cls.datefmt(date))
            lessons_str = '\n'.join(str(self.formatter_cls(l)) for l in query)
            return [Response(message_str),
                    Response(lessons_str)]
        return self.no_lessons_response()


schedule = Router({
    is_student: StudentSchedule.handle,
    is_teacher: TeacherSchedule.handle,
}, name=state_name(Schedule))


cases = gen_state_cases([
    schedule,
    Settings,
    RequiredGroupInput,
    RequiredSubGroupInput,
    RequiredNameInput,
    SettingsLanguageInput,
    SettingsNameInput,
    SettingsGroupInput,
    SettingsSubgroupInput,
])
