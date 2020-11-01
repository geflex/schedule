from functools import cached_property

from bottex2.chat import Button, Keyboard
from bottex2.router import Router, text_cond
from bottex2.handler import Request
from bottex2.views import View, Command

from schedule.models import PType
from schedule._logic import Date


schedule_kb = Keyboard([
    [Button('Сегодня')],
    [Button('Завтра')],
    [Button('Настройки')],
])


async def name_after_switching_ptype(r: Request):
    await r.chat.send_message('Теперь ты препод', Settings(r).keyboard)
    await r.user.update(name=r.text, state=Settings.name)


async def group_after_switching_ptype(r: Request):
    await r.chat.send_message('Теперь ты студент', Settings(r).keyboard)
    await r.user.update(group=r.text, state=Settings.name)


# =====================================================


class Settings(View):
    name = 'settings'
    
    @cached_property
    def commands(self):
        commands = []
        def add(text, cb):
            commands.append([Command(text, cb)])

        if self.r.user.ptype is PType.teacher:
            add('Стать студентом', become_student)
            add('Изменить ФИО', switch_to_settings_name)
        else:
            add('Стать преподом', become_teacher)
            add('Изменить группу', switch_to_settings_group)
            add('Изменить подгруппу', switch_to_settings_subgroup)
        add('Назад', switch_to_schedule)
        return commands


class BaseInput(View):
    @cached_property
    def commands(self):
        return [[Command('Не менять', settings_cancel_input)]]


class SettingsGroup(BaseInput):
    async def default(self, r: Request):
        old_group = r.user.group
        await r.user.update(group=r.text, state=Settings.name)
        await r.chat.send_message(f'Группа изменена с {old_group} на {r.user.group}',
                                  Settings(r).keyboard)


class SettingsName(BaseInput):
    async def default(self, r: Request):
        old_name = r.user.name
        await r.user.update(name=r.text, state=Settings.name)
        await r.chat.send_message(f'Имя изменено с {old_name} на {r.user.name}',
                                  Settings(r).keyboard)


class SettingsSubgroup(BaseInput):
    async def default(self, r: Request):
        old_subgroup = r.user.subgroup
        await r.user.update(subgroup=r.text, state=Settings.name)
        await r.chat.send_message(f'Подгруппа изменена с {old_subgroup} на {r.user.subgroup}',
                                  Settings(r).keyboard)


async def switch_to_settings_group(r: Request):
    await r.chat.send_message(f'Текущая группа: {r.user.group}\nВведи номер группы', SettingsGroup(r).keyboard)
    await r.user.update(state=SettingsGroup.name)


async def switch_to_settings_name(r: Request):
    await r.chat.send_message(f'Текущее имя: {r.user.name}\nВведи новое имя', SettingsName(r).keyboard)
    await r.user.update(state=SettingsName.name)


async def switch_to_settings_subgroup(r: Request):
    await r.chat.send_message(f'Текущая подгруппа: {r.user.subgroup}\nВведи номер подгруппы', SettingsSubgroup(r).keyboard)
    await r.user.update(state=SettingsSubgroup.name)


async def settings_cancel_input(r: Request):
    await r.chat.send_message('Ладно', Settings(r).keyboard)
    await r.user.update(state=Settings.name)


# =====================================================


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


unknown_command_str = 'Хм непонятная команда'


async def today(r: Request):
    date = Date.today().strftime('%d.%m.%Y')
    await r.chat.send_message(f'Так расписание для {r.user.group} на {date}', schedule_kb)


async def tomorrow(r: Request):
    date = Date.tomorrow().strftime('%d.%m.%Y')
    await r.chat.send_message(f'Так расписание для {r.user.group} на {date}', schedule_kb)


async def switch_to_schedule(r: Request):
    await r.chat.send_message('Главное меню', schedule_kb)
    await r.user.update(state=schedule.__name__)


async def unknown_settings_command(r: Request):
    await r.chat.send_message(unknown_command_str, Settings(r).keyboard)


async def switch_to_settings(r: Request):
    await r.chat.send_message('Настройки', Settings(r).keyboard)
    await r.user.update(state=Settings.name)


async def unknown_schedule_command(r: Request):
    await r.chat.send_message(unknown_command_str, schedule_kb)


schedule = Router({
    text_cond('сегодня'): today,
    text_cond('завтра'): tomorrow,
    text_cond('настройки'): switch_to_settings,
}, default=unknown_schedule_command, name='schedule')
