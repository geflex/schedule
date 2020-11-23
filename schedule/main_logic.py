from abc import abstractmethod, ABC
from functools import cached_property, partial
from typing import List, Type

import sqlalchemy as sa

from bottex2.ext.users import gen_state_cases
from bottex2.handler import Request
from bottex2.helpers.tools import state_name
from bottex2.router import Router
from bottex2.views import View, Command
from . import dateutils
from . import inputs
from . import models as m
from .dateutils import Date
from .models import PType, i18n, Lang

_ = i18n.gettext
_c = i18n.rgettext


def group_str(group):
    return group.name if group else ''


def ptype_cond(ptype: PType):
    def cond(r):
        return r.user.ptype is ptype
    return cond

is_student = ptype_cond(PType.student)
is_teacher = ptype_cond(PType.teacher)


class Settings(View):
    state_name = 'settings'
    
    @cached_property
    def commands(self):
        commands = []
        def add(text, cb):
            commands.append([Command(text, cb)])

        add(_c('Изменить язык'), SettingsLanguageInput.switch)
        if self.r.user.ptype is PType.teacher:
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
        return r.resp(_('Настройки'), Settings(r).keyboard)


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
            return r.resp(
                _('Язык изменен с {} на {}').format(old.value, lang.value),
                Settings(r).keyboard
            )
        return setter

    @classmethod
    async def switch(cls, r: Request):
        kb = cls(r).keyboard
        current = r.user.locale
        await super().switch(r)
        return [r.resp(_('Текущий язык: {}').format(current.value), kb),
                r.resp(_('Выбери новый язык'), kb)]


class SettingsGroupInput(inputs.BaseGroupInput, BaseSettingsInput):
    state_name = 'settings_group'

    @property
    def commands(self) -> List[List[Command]]:
        commands = super().commands
        commands2 = super(inputs.BaseGroupInput, self).commands
        return commands + commands2

    async def set_group(self, r: Request):
        old = r.user.group
        try:
            await super().set_group(r)
        except inputs.ErrorResponse as e:
            return e.resp
        await r.user.update(state=state_name(Settings))
        return r.resp(
            _('Группа изменена с {} на {}').format(group_str(old), group_str(r.user.group)),
            Settings(r).keyboard
        )

    @classmethod
    async def switch(cls, r: Request):
        kb = cls(r).keyboard
        await super().switch(r)
        return [r.resp(_('Текущая группа: {}').format(group_str(r.user.group)), kb),
                r.resp(_('Введи номер группы'), kb)]


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
        return r.resp(_('Имя изменено с {} на {}').format(old, r.text),
                        Settings(r).keyboard)

    @classmethod
    async def switch(cls, r: Request):
        kb = cls(r).keyboard
        await super().switch(r)
        return [r.resp(_('Текущее имя: {}').format(r.user.name), kb),
                r.resp(_('Введи новое имя'), kb)]


class SettingsSubgroupInput(inputs.BaseSubgroupInput, BaseSettingsInput):
    state_name = 'settings_subgroup'

    @cached_property
    def commands(self):
        commands = super().commands
        commands2 = super(inputs.BaseSubgroupInput, self).commands
        return commands + commands2

    def get_subgroup_setter(self, subgroup_num: str):
        super_setter = super().get_subgroup_setter(subgroup_num)
        async def setter(r: Request):
            old = r.user.subgroup
            await super_setter(r)
            await r.user.update(state=state_name(Settings))
            return r.resp(
                _('Подгруппа изменена с {} на {}').format(old, subgroup_num),
                Settings(r).keyboard
            )
        return setter

    @classmethod
    async def switch(cls, r: Request):
        kb = cls(r).keyboard
        await super().switch(r)
        return [r.resp(_('Текущая подгруппа: {}').format(r.user.subgroup), kb),
                r.resp(_('Введи номер подгруппы'), kb)]


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
        try:
            result = await super().set_group(r)
        except inputs.ErrorResponse as e:
            return e.resp
        if not r.user.subgroup:
            return await RequiredSubGroupInput.switch(r)
        return await save_student(r)

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        return r.resp(_('Введи номер группы'), cls(r).keyboard)


class RequiredSubGroupInput(inputs.BaseSubgroupInput, BasePTypeRequiredInput):
    state_name = 'subgroup_after_switching_ptype'

    @cached_property
    def commands(self) -> List[List[Command]]:
        choises = super().commands
        commands = super(inputs.BaseSubgroupInput, self).commands
        return choises + commands

    def get_subgroup_setter(self, subgroup_num: str):
        super_setter = super().get_subgroup_setter(subgroup_num)
        async def setter(r: Request):
            await super_setter(r)
            return await save_student(r)
        return setter

    async def cancel(self, r: Request):
        await r.user.update(ptype=PType.teacher)
        return await Settings.switch(r)

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        return r.resp(_('Выбери подгруппу'), cls(r).keyboard)


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
        return r.resp(_('Введи имя'), cls(r).keyboard)


async def save_teacher(r: Request):
    await r.user.update(state=state_name(Settings), ptype=PType.teacher)
    return r.resp(_('Включен режим преподавателя'), Settings(r).keyboard)


async def save_student(r: Request):
    await r.user.update(state=state_name(Settings), ptype=PType.student)
    return r.resp(_('Включен режим студента'), Settings(r).keyboard)


class LessonFormatter(ABC):
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
            return self.lesson.places[0].building.name
        return '?'

    def auditory(self):
        return ''.join(a.auditory for a in self.lesson.places) or '?'

    def teacher(self):
        return ', '.join(t.last_name for t in self.lesson.teachers)

    @abstractmethod
    def __str__(self):
        pass


class TeacherFormatter(LessonFormatter):
    def __str__(self):
        subgroup = f' ({self.subgroup()})'
        return f'{self.time()} {self.name()} {self.building()} {self.auditory()} {self.group()}{subgroup}'


class StudentFormatter(LessonFormatter):
    def __str__(self):
        return f'{self.time()} {self.name()} {self.building()} {self.auditory()} {self.teacher()}'


class Schedule(View, ABC):
    formatter_cls: Type[LessonFormatter]
    state_name = 'schedule'

    @property
    def commands(self):
        return [
            [Command(_c('Сегодня'), self.today),
             Command(_c('Завтра'), self.tomorrow)],
            [Command(_c('Настройки'), Settings.switch)],
        ]

    async def default(self, r: Request):
        return r.resp(_('Непонятная команда'), self.keyboard)

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        return r.resp(_('Главное меню'), cls(r).keyboard)

    def query_conditions(self, date):
        week_cond = sa.or_(m.Lesson.second_weeknum == dateutils.is_second_weeknum(date),
                           m.Lesson.second_weeknum == None)
        weekday_cond = m.Lesson.weekday == m.Weekday(date.weekday())
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

    def no_lessons(self):
        return self.r.resp(_('Занятий нет)'), self.keyboard)


def datefmt(date):
    return date.strftime("%d.%m.%Y")


class TeacherSchedule(Schedule):
    formatter_cls = TeacherFormatter

    def _schedule(self, date: Date, r: Request):
        resp = partial(r.resp, kb=self.keyboard)
        user = r.user

        query = m.Lesson.query().filter(
            m.Lesson.teachers.any(last_name=user.name),
            *self.query_conditions(date),
        ).all()
        if query:
            message_str = _('Преподаватель {}\n'
                            'День {}').format(user.name, datefmt(date))
            lessons_str = '\n'.join(str(self.formatter_cls(l)) for l in query)
            return [resp(message_str),
                    resp(lessons_str)]
        return self.no_lessons()


class StudentSchedule(Schedule):
    formatter_cls = StudentFormatter

    def _schedule(self, date: Date, r: Request):
        resp = partial(r.resp, kb=self.keyboard)
        user = r.user

        query = m.Lesson.query().filter(
            m.Lesson.groups.any(name=user.group.name),
            sa.or_(
                m.Lesson.subgroup == user.subgroup,
                m.Lesson.subgroup == None,
            ),
            *self.query_conditions(date),
        ).all()
        if query:
            message_str = _('Группа {}\n'
                            'Подгруппа {}\n'
                            'День {}').format(user.group.name, user.subgroup, datefmt(date))
            lessons_str = '\n'.join(str(self.formatter_cls(l)) for l in query)
            return [resp(message_str),
                    resp(lessons_str)]
        return self.no_lessons()


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
