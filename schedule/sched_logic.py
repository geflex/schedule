from functools import cached_property
import re

from bottex2.chat import Keyboard
from bottex2.handler import Request
from bottex2.helpers.tools import state_name
from bottex2.router import Router, regexp_cond
from bottex2.views import View, Command
from bottex2.helpers import regexp

from schedule.models import PType
from schedule.db_api import Date


class Settings(View):
    name = 'settings'
    
    @cached_property
    def commands(self):
        commands = []
        def add(text, cb):
            commands.append([Command(text, cb)])

        if self.r.user.ptype is PType.teacher:
            add('Стать студентом', become_student)
            add('Изменить ФИО', SettingsNameInput.switch)
        else:
            add('Стать преподом', become_teacher)
            add('Изменить группу', SettingsGroupInput.switch)
            add('Изменить подгруппу', SettingsSubgroupInput.switch)
        add('Назад', Schedule.switch)
        return commands

    @classmethod
    async def switch(cls, r: Request):
        await r.chat.send_message('Настройки', Settings(r).keyboard)
        await super().switch(r)


class SettingsInput(View):
    @cached_property
    def commands(self):
        return [[Command('Не менять', self.back)]]

    @classmethod
    async def back(cls, r: Request):
        await r.chat.send_message('Ладно', Settings(r).keyboard)
        await r.user.update(state=state_name(Settings))


class SettingsGroupInput(SettingsInput):
    name = 'settings_group'
    exp = re.compile(r'\d{8}')
    revexp = regexp.compile(exp)

    @cached_property
    def router(self) -> Router:
        router = super().router
        router.add_route(regexp_cond(self.exp), self.set_subgroup)
        return router

    async def set_subgroup(self, r: Request):
        old_group = r.user.group
        await r.user.update(group=r.text, state=state_name(Settings))
        await r.chat.send_message(f'Группа изменена с {old_group} на {r.user.group}',
                                  Settings(r).keyboard)

    @classmethod
    async def switch(cls, r: Request):
        kb = cls(r).keyboard
        await r.chat.send_message(f'Текущая группа: {r.user.group}', kb)
        await r.chat.send_message('Введи номер группы', kb)
        await super().switch(r)

    async def default(self, r: Request):
        await r.chat.send_message(f'Номер группы должен состоять из 8 цифр', self.keyboard)


class SettingsNameInput(SettingsInput):
    name = 'settings_name'

    async def default(self, r: Request):
        old_name = r.user.name
        await r.user.update(name=r.text, state=state_name(Settings))
        await r.chat.send_message(f'Имя изменено с {old_name} на {r.user.name}',
                                  Settings(r).keyboard)

    @classmethod
    async def switch(cls, r: Request):
        kb = cls(r).keyboard
        await r.chat.send_message(f'Текущее имя: {r.user.name}', kb)
        await r.chat.send_message('Введи новое имя', kb)
        await super().switch(r)


class SettingsSubgroupInput(SettingsInput):
    name = 'settings_subgroup'

    @cached_property
    def commands(self):
        commands = [[
            Command('Первая', self.get_subgroup_setter('1')),
            Command('Вторая', self.get_subgroup_setter('2')),
        ]]
        return commands

    def get_subgroup_setter(self, subgroup_num: str):
        async def subgroup_setter(r: Request):
            old_subgroup = r.user.subgroup
            await r.user.update(subgroup=subgroup_num, state=state_name(Settings))
            await r.chat.send_message(f'Подгруппа изменена с {old_subgroup} на {r.user.subgroup}',
                                      Settings(r).keyboard)
        return subgroup_setter

    @classmethod
    async def switch(cls, r: Request):
        kb = cls(r).keyboard
        await r.chat.send_message(f'Текущая подгруппа: {r.user.subgroup}', kb)
        await r.chat.send_message('Введи номер подгруппы', kb)
        await super().switch(r)


async def name_after_switching_ptype(r: Request):
    await r.chat.send_message('Теперь ты препод', Settings(r).keyboard)
    await r.user.update(name=r.text, state=state_name(Settings))


async def group_after_switching_ptype(r: Request):
    await r.chat.send_message('Теперь ты студент', Settings(r).keyboard)
    await r.user.update(group=r.text, state=state_name(Settings))


async def become_teacher(r: Request):
    await r.user.update(ptype=PType.teacher)
    if r.user.name:
        await r.chat.send_message('Теперь ты препод', Settings(r).keyboard)
    else:
        await r.chat.send_message('Введи свои ФИО', Keyboard())
        await r.user.update(state=name_after_switching_ptype.__name__)


async def become_student(r: Request):
    await r.user.update(ptype=PType.student)
    if r.user.group:
        await r.chat.send_message('Теперь ты студент', Settings(r).keyboard)
    else:
        await r.chat.send_message('Введи номер группы', Keyboard())
        await r.user.update(state=group_after_switching_ptype.__name__)


class Schedule(View):
    name = 'schedule'

    @cached_property
    def commands(self):
        return [
            [Command('Сегодня', self.today)],
            [Command('Завтра', self.tomorrow)],
            [Command('Настройки', Settings.switch)],
        ]

    async def default(self, r: Request):
        await r.chat.send_message('Непонятная команда', self.keyboard)

    @classmethod
    async def switch(cls, r: Request):
        await r.chat.send_message('Главное меню', cls(r).keyboard)
        await super().switch(r)

    async def _schedule(self, date: Date, r: Request):
        if r.user.ptype is PType.student:
            who = r.user.group
        else:
            who = r.user.name

        await r.chat.send_message(f'Так расписание для {who} на {date.strftime("%d.%m.%Y")}',
                                  self.keyboard)

    @classmethod
    async def today(cls, r: Request):
        date = Date.today()
        await cls(r)._schedule(date, r)

    @classmethod
    async def tomorrow(cls, r: Request):
        date = Date.tomorrow()
        await cls(r)._schedule(date, r)
