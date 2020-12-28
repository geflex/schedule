from abc import abstractmethod, ABC
from typing import List, Type

import sqlalchemy as sa

from bottex2.handler import Request, Response, Handler
from bottex2.router import Router
from bottex2.states import state_name, gen_state_cases
from bottex2.views import View, Command
from . import dateutils
from . import inputs
from . import models as m
from .dateutils import Date
from .models import i18n, Lang, Weekday, Subgroup, PType

_ = i18n.gettext
_c = i18n.rgettext


def ptype_cond(ptype: PType):
    def cond(r):
        return r.user.ptype is ptype
    return cond

is_student = ptype_cond(PType['student'])
is_teacher = ptype_cond(PType['teacher'])


class Settings(View, ABC):
    state_name = 'settings'

    def commands(self):
        commands = [
            [Command(_c('Изменить язык'), SettingsLanguageInput.switcher)],
            [Command(_c('Назад'), Schedule.switcher)],
        ]
        return commands

    async def switch(self):
        await super().switch()
        return Response(_('Настройки'))


class StudentSettings(Settings):
    def commands(self):
        commands = [
            [Command(_c('Режим преподавателя'), self.become_teacher)],
            [Command(_c('Изменить группу'), SettingsGroupInput.switcher)],
            [Command(_c('Изменить подгруппу'), SettingsSubgroupInput.switcher)],
        ]
        return commands + super().commands()

    @staticmethod
    def become_teacher(r: Request):
        if not r.user.name:
            return RequiredNameInput.switcher(r)
        else:
            return save_teacher(r)


class TeacherSettings(Settings):
    def commands(self):
        commands = [
            [Command(_c('Режим студента'), self.become_student)],
            [Command(_c('Изменить имя'), SettingsNameInput.switcher)],
        ]
        return commands + super().commands()

    @staticmethod
    def become_student(r: Request):
        if not r.user.group:
            return RequiredGroupInput.switcher(r)
        if not r.user.subgroup:
            return RequiredSubGroupInput.switcher(r)
        else:
            return save_student(r)


class BaseSettingsInput(View):
    def commands(self):
        return [[Command(_c('Отмена'), Settings.switcher)]]


class SettingsLanguageInput(inputs.BaseLanguageInput, BaseSettingsInput):
    state_name = 'settings_lang'

    def commands(self):
        commands = super().commands()
        commands2 = super(inputs.BaseLanguageInput, self).commands()
        return commands + commands2

    @classmethod
    def get_lang_setter(cls, lang: Lang):
        super_setter = super().get_lang_setter(lang)
        async def setter(r: Request):
            old_lang = r.user.locale
            await super_setter(r)
            await r.user.set_state(Settings)
            return Response(
                _('Язык изменен с {} на {}').format(old_lang.name, lang.name),
                Settings(r).keyboard
            )
        return setter

    async def switch(self):
        current_lang = self.r.user.locale  # type: Lang
        await super().switch()
        return [Response(_('Текущий язык: {}').format(current_lang.name)),
                Response(_('Выбери новый язык'))]


class SettingsGroupInput(inputs.BaseGroupInput, BaseSettingsInput):
    state_name = 'settings_group'

    def commands(self) -> List[List[Command]]:
        commands = super().commands()
        commands2 = super(inputs.BaseGroupInput, self).commands()
        return commands + commands2

    @staticmethod
    def group_str(group):
        return group.name if group else ''

    @classmethod
    async def set_group(cls, r: Request):
        old_group = r.user.group
        await super().set_group(r)
        await r.user.set_state(Settings)
        return Response(
            _('Группа изменена с {} на {}').format(cls.group_str(old_group),
                                                   cls.group_str(r.user.group)),
            Settings(r).keyboard
        )

    async def switch(self):
        await super().switch()
        return [Response(_('Текущая группа: {}').format(self.group_str(self.r.user.group))),
                Response(_('Введи номер группы'))]


class SettingsNameInput(inputs.BaseNameInput, BaseSettingsInput):
    state_name = 'settings_name'

    def commands(self) -> List[List[Command]]:
        commands = super().commands()
        commands2 = super(inputs.BaseNameInput, self).commands()
        return commands + commands2

    @classmethod
    async def set_name(cls, r: Request):
        old_name = r.user.name
        await super().set_name(r)
        await r.user.set_state(Settings)
        return Response(_('Имя изменено с {} на {}').format(old_name, r.text),
                        Settings(r).keyboard)

    async def switch(self):
        await super().switch()
        return [Response(_('Текущее имя: {}').format(self.r.user.name)),
                Response(_('Введи новое имя'))]


class SettingsSubgroupInput(inputs.BaseSubgroupInput, BaseSettingsInput):
    state_name = 'settings_subgroup'

    def commands(self):
        commands = super().commands()
        commands2 = super(inputs.BaseSubgroupInput, self).commands()
        return commands + commands2

    @classmethod
    def get_subgroup_setter(cls, subgroup: Subgroup):
        super_setter = super().get_subgroup_setter(subgroup)
        async def setter(r: Request):
            old_subgroup = r.user.subgroup
            await super_setter(r)
            await r.user.set_state(Settings)
            return Response(
                _('Подгруппа изменена с {} на {}').format(old_subgroup.name, subgroup.name),
                Settings(r).keyboard
            )
        return setter

    async def switch(self):
        await super().switch()
        return [Response(_('Текущая подгруппа: {}').format(self.r.user.subgroup.name)),
                Response(_('Введи номер подгруппы'))]


class BasePTypeRequiredInput(BaseSettingsInput):
    def commands(self) -> List[List[Command]]:
        return [[Command(_c('Отмена'), self.cancel)]]

    @staticmethod
    def cancel(r: Request):
        return Settings.switcher(r)


class RequiredGroupInput(inputs.BaseGroupInput, BasePTypeRequiredInput):
    state_name = 'group_after_switching_ptype'

    def commands(self):
        commands = super().commands()
        commands2 = super(inputs.BaseGroupInput, self).commands()
        return commands + commands2

    @classmethod
    async def set_group(cls, r: Request):
        result = await super().set_group(r)
        if not r.user.subgroup:
            return await RequiredSubGroupInput.switcher(r)
        return await save_student(r)

    async def switch(self):
        await super().switch()
        return Response(_('Введи номер группы'))


class RequiredSubGroupInput(inputs.BaseSubgroupInput, BasePTypeRequiredInput):
    state_name = 'subgroup_after_switching_ptype'

    def commands(self) -> List[List[Command]]:
        choises = super().commands()
        commands = super(inputs.BaseSubgroupInput, self).commands()
        return choises + commands

    @classmethod
    def get_subgroup_setter(cls, subgroup: Subgroup):
        super_setter = super().get_subgroup_setter(subgroup)
        async def setter(r: Request):
            await super_setter(r)
            return await save_student(r)
        return setter

    @staticmethod
    async def cancel(r: Request):
        await r.user.update(ptype=PType['teacher'])
        return await Settings.switcher(r)

    async def switch(self):
        await super().switch()
        return Response(_('Выбери подгруппу'))


class RequiredNameInput(inputs.BaseNameInput, BasePTypeRequiredInput):
    state_name = 'name_after_switching_ptype'

    def commands(self):
        commands = super().commands()
        commands2 = super(inputs.BaseNameInput, self).commands()
        return commands + commands2

    @classmethod
    async def set_name(cls, r: Request):
        await super().set_name(r)
        return await save_teacher(r)

    async def switch(self):
        await super().switch()
        return Response(_('Введи имя'))


async def save_teacher(r: Request):
    await r.user.update(state=state_name(TeacherSettings), ptype=PType['teacher'])
    return Response(_('Включен режим преподавателя'), TeacherSettings(r).keyboard)


async def save_student(r: Request):
    await r.user.update(state=state_name(StudentSettings), ptype=PType['student'])
    return Response(_('Включен режим студента'), StudentSettings(r).keyboard)


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

    def commands(self):
        return [
            [Command(_c('Сегодня'), self.today), Command(_c('Завтра'), self.tomorrow)],
            [Command(_c(wd.short_name.capitalize()), self.weekday(wd)) for wd in list(Weekday)],
            [Command(_c('Настройки'), Settings.switcher)],
        ]

    async def default(self, r: Request):
        return Response(_('Непонятная команда'))

    async def switch(self):
        await super().switch()
        return Response(_('Главное меню'))

    @staticmethod
    def _query_conditions(date):
        # noinspection PyComparisonWithNone
        week_cond = sa.or_(m.Lesson.second_weeknum == dateutils.is_second_weeknum(date),
                           m.Lesson.second_weeknum == None)
        weekday_cond = (m.Lesson.weekday_num == date.weekday())
        return week_cond, weekday_cond

    @classmethod
    async def _schedule(cls, date: Date, r: Request):
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

    @staticmethod
    def no_lessons_response() -> Response:
        return Response(_('Занятий нет)'))


class TeacherSchedule(Schedule):
    formatter_cls = TeacherFormatter

    @classmethod
    def _schedule(cls, date: Date, r: Request):
        user = r.user

        query = m.Lesson.query.filter(
            m.Lesson.teachers.any(last_name=user.name),
            *cls._query_conditions(date),
        )
        query = query.all()
        if query:
            message_str = _('Преподаватель {}\n'
                            '{}').format(user.name, cls.formatter_cls.datefmt(date))
            lessons_str = '\n'.join(str(cls.formatter_cls(l)) for l in query)
            return [Response(message_str),
                    Response(lessons_str)]
        return cls.no_lessons_response()


class StudentSchedule(Schedule):
    formatter_cls = StudentFormatter

    @classmethod
    def _schedule(cls, date: Date, r: Request):
        user = r.user

        # noinspection PyComparisonWithNone
        query = m.Lesson.query.filter(
            m.Lesson.groups.any(name=user.group.name),
            sa.or_(
                m.Lesson.subgroup == user.subgroup,
                m.Lesson.subgroup == None,
            ),
            *cls._query_conditions(date),
        )
        query = query.all()
        if query:
            message_str = _('Группа {}\n'
                            '{} подгруппа\n'
                            '{}').format(user.group.name,
                                         user.subgroup.name,
                                         cls.formatter_cls.datefmt(date))
            lessons_str = '\n'.join(str(cls.formatter_cls(l)) for l in query)
            return [Response(message_str),
                    Response(lessons_str)]
        return cls.no_lessons_response()


schedule = Router({
    is_student: StudentSchedule.handle,
    is_teacher: TeacherSchedule.handle,
}, name=state_name(Schedule))

settings = Router({
    is_student: StudentSettings.handle,
    is_teacher: TeacherSettings.handle,
}, name=state_name(Settings))


cases = gen_state_cases([
    schedule,
    settings,
    RequiredGroupInput,
    RequiredSubGroupInput,
    RequiredNameInput,
    SettingsLanguageInput,
    SettingsNameInput,
    SettingsGroupInput,
    SettingsSubgroupInput,
])
