from functools import cached_property, partial
from typing import List

from bottex2.ext.i18n import gettext, rgettext
from bottex2.ext.users import gen_state_cases
from bottex2.handler import Request
from bottex2.helpers.tools import state_name
from bottex2.views import View, Command
from schedule.db_api import Date
from schedule.models import PType
from . import inputs
from .models import Lang

_ = partial(gettext, domain='schedule')
_c = rgettext


class Settings(View):
    name = 'settings'
    
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
        return [[Command(_c('Отмена'), self.back)]]

    @classmethod
    async def back(cls, r: Request):
        await r.user.update(state=state_name(Settings))
        return r.resp(_('Ладно'), Settings(r).keyboard)


class SettingsLanguageInput(inputs.BaseLanguageInput, BaseSettingsInput):
    name = 'settings_lang'

    @cached_property
    def commands(self):
        commands = super().commands
        commands.extend(super(inputs.BaseLanguageInput, self).commands)
        return commands

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
        await r.chat.send_message(_('Текущий язык: {}').format(current.value), kb)
        await r.chat.send_message(_('Выбери новый язык'), kb)
        await super().switch(r)


class SettingsGroupInput(inputs.BaseGroupInput, BaseSettingsInput):
    name = 'settings_group'

    async def set_group(self, r: Request):
        old = r.user.group
        await super().set_group(r)
        await r.user.update(state=state_name(Settings))
        return r.resp(
            _('Группа изменена с {} на {}').format(old, r.user.group),
            Settings(r).keyboard
        )

    @classmethod
    async def switch(cls, r: Request):
        kb = cls(r).keyboard
        await r.chat.send_message(_('Текущая группа: {}').format(r.user.group), kb)
        await r.chat.send_message(_('Введи номер группы'), kb)
        await super().switch(r)


class SettingsNameInput(inputs.BaseNameInput, BaseSettingsInput):
    name = 'settings_name'

    @cached_property
    def commands(self):
        return []

    async def set_name(self, r: Request):
        old = r.user.name
        await super().set_name(r)
        await r.user.update(state=state_name(Settings))
        return r.resp(_('Имя изменено с {} на {}').format(old, r.text),
                        Settings(r).keyboard)

    @classmethod
    async def switch(cls, r: Request):
        kb = cls(r).keyboard
        await r.chat.send_message(_('Текущее имя: {}').format(r.user.name), kb)
        await r.chat.send_message(_('Введи новое имя'), kb)
        await super().switch(r)


class SettingsSubgroupInput(inputs.BaseSubgroupInput, BaseSettingsInput):
    name = 'settings_subgroup'

    @cached_property
    def commands(self):
        commands = super().commands
        commands.extend(super(inputs.BaseSubgroupInput, self).commands)
        return commands

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
        await r.chat.send_message(_('Текущая подгруппа: {}').format(r.user.subgroup), kb)
        await r.chat.send_message(_('Введи номер подгруппы'), kb)
        await super().switch(r)


class BasePTypeRequiredInput(BaseSettingsInput):
    @property
    def commands(self) -> List[List[Command]]:
        return [[Command(_c('Отмена'), self.cancel)]]

    async def cancel(self, r: Request):
        return await Settings.switch(r)


class RequiredGroupInput(inputs.BaseGroupInput, BasePTypeRequiredInput):
    name = 'group_after_switching_ptype'

    async def set_group(self, r: Request):
        await super().set_group(r)
        if not r.user.subgroup:
            return await RequiredSubGroupInput.switch(r)
        return await save_student(r)

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        return r.resp(_('Введи номер группы'), cls(r).keyboard)


class RequiredSubGroupInput(inputs.BaseSubgroupInput, BasePTypeRequiredInput):
    name = 'subgroup_after_switching_ptype'

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
    name = 'name_after_switching_ptype'

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


class Schedule(View):
    name = 'schedule'

    @cached_property
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

    async def _schedule(self, date: Date, r: Request):
        if r.user.ptype is PType.student:
            who = r.user.group
        else:
            who = r.user.name

        return r.resp(
            _('Расписание для {} на {}').format(who, date.strftime("%d.%m.%Y")),
            self.keyboard
        )

    @classmethod
    async def today(cls, r: Request):
        date = Date.today()
        return await cls(r)._schedule(date, r)

    @classmethod
    async def tomorrow(cls, r: Request):
        date = Date.tomorrow()
        return await cls(r)._schedule(date, r)


cases = gen_state_cases([
    Schedule,
    Settings,
    RequiredGroupInput,
    RequiredSubGroupInput,
    RequiredNameInput,
    SettingsLanguageInput,
    SettingsNameInput,
    SettingsGroupInput,
    SettingsSubgroupInput,
])
