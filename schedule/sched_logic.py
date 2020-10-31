from bottex2.chat import Button, Keyboard
from bottex2.router import Router, text_cond
from bottex2.handler import Request

from schedule.models import PType
from schedule._logic import Date


schedule_kb = Keyboard([
    [Button('Сегодня')],
    [Button('Завтра')],
    [Button('Настройки')],
])


async def name_after_switching_ptype(r: Request):
    await r.chat.send_message('Теперь ты препод', get_settings_kb(r))
    await r.user.update(name=r.text, state=settings.__name__)


async def group_after_switching_ptype(r: Request):
    await r.chat.send_message('Теперь ты студент', get_settings_kb(r))
    await r.user.update(group=r.text, state=settings.__name__)


# =====================================================


async def switch_to_settings_group(r: Request):
    await r.chat.send_message(f'Текущая группа: {r.user.group}\nВведи номер группы', Keyboard())
    await r.user.update(state=settings_group.__name__)


async def switch_to_settings_name(r: Request):
    await r.chat.send_message(f'Текущее имя: {r.user.name}\nВведи новое имя', Keyboard())
    await r.user.update(state=settings_name.__name__)


async def switch_to_settings_subgroup(r: Request):
    await r.chat.send_message(f'Текущая подгруппа: {r.user.subgroup}\nВведи номер подгруппы', Keyboard())
    await r.user.update(state=settings_subgroup.__name__)


async def settings_group_input(r: Request):
    old_group = r.user.group
    await r.user.update(group=r.text, state=settings.__name__)
    await r.chat.send_message(f'Группа изменена с {old_group} на {r.user.group}', get_settings_kb(r))


async def settings_name_input(r: Request):
    old_name = r.user.name
    await r.user.update(name=r.text, state=settings.__name__)
    await r.chat.send_message(f'Имя изменено с {old_name} на {r.user.name}', get_settings_kb(r))


async def settings_subgroup_input(r: Request):
    old_subgroup = r.user.subgroup
    await r.user.update(subgroup=r.text, state=settings.__name__)
    await r.chat.send_message(f'Подгруппа изменена с {old_subgroup} на {r.user.subgroup}', get_settings_kb(r))


async def settings_cancel_input(r: Request):
    await r.chat.send_message('Ладно')
    await r.user.update(state=settings.__name__)


no_change_label = 'Не менять'
input_kb = Keyboard([[Button(no_change_label)]])
input_commands = {text_cond(no_change_label): settings_cancel_input}
settings_group = Router(input_commands, default=settings_group_input)
settings_name = Router(input_commands, default=settings_name_input)
settings_subgroup = Router(input_commands, default=settings_subgroup_input)


# =====================================================


async def become_teacher(r: Request):
    await r.user.update(ptype=PType.teacher)
    if r.user.name:
        await r.chat.send_message('Теперь ты препод', get_settings_kb(r))
    else:
        await r.chat.send_message('Введи свои ФИО', Keyboard())
        await r.user.update(state=name_after_switching_ptype.__name__)


async def become_student(r: Request):
    await r.user.update(ptype=PType.student)
    if r.user.group:
        await r.chat.send_message('Теперь ты студент', get_settings_kb(r))
    else:
        await r.chat.send_message('Введи номер группы', Keyboard())
        await r.user.update(state=group_after_switching_ptype.__name__)


def get_settings_kb(r: Request):
    keyboard = Keyboard()
    if r.user.ptype is PType.teacher:
        keyboard.add_line(Button('Стать студентом'))
        keyboard.add_line(Button('Изменить ФИО'))
    else:
        keyboard.add_line(Button('Стать преподом'))
        keyboard.add_line(Button('Изменить группу'))
        keyboard.add_line(Button('Изменить подгруппу'))
    keyboard.add_line(Button('Назад'))
    return keyboard


async def settings(r: Request):
    router = Router(default=unknown_settings_command, name='settings')
    if r.user.ptype is PType.teacher:
        router.add_route(text_cond('Стать студентом'), become_student)
        router.add_route(text_cond('Изменить ФИО'), switch_to_settings_name)
    else:
        router.add_route(text_cond('Стать преподом'), become_teacher)
        router.add_route(text_cond('Изменить группу'), switch_to_settings_group)
        router.add_route(text_cond('Изменить подгруппу'), switch_to_settings_subgroup)
    router.add_route(text_cond('Назад'), switch_to_schedule)
    return await router(r)


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
    await r.chat.send_message(unknown_command_str, get_settings_kb(r))


async def switch_to_settings(r: Request):
    await r.chat.send_message('Настройки', get_settings_kb(r))
    await r.user.update(state=settings.__name__)


async def unknown_schedule_command(r: Request):
    await r.chat.send_message(unknown_command_str, schedule_kb)


schedule = Router({
    text_cond('сегодня'): today,
    text_cond('завтра'): tomorrow,
    text_cond('настройки'): switch_to_settings,
}, default=unknown_schedule_command, name='schedule')
