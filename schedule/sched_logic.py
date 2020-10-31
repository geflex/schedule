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


async def name_settings_input(r: Request):
    await r.chat.send_message('Теперь ты препод', get_settings_kb(r))
    await r.user.update(name=r.text, state=settings.__name__)


async def group_settings_input(r: Request):
    await r.chat.send_message('Теперь ты студент', get_settings_kb(r))
    await r.user.update(group=r.text, state=settings.__name__)


async def become_teacher(r: Request):
    await r.user.update(ptype=PType.teacher)
    if r.user.name:
        await r.chat.send_message('Теперь ты препод', get_settings_kb(r))
    else:
        await r.chat.send_message('Введи свои ФИО', Keyboard())
        await r.user.update(state=name_settings_input.__name__)


async def become_student(r: Request):
    await r.user.update(ptype=PType.student)
    if r.user.group:
        await r.chat.send_message('Теперь ты студент', get_settings_kb(r))
    else:
        await r.chat.send_message('Введи номер группы', Keyboard())
        await r.user.update(state=group_settings_input.__name__)


def get_settings_kb(r: Request):
    keyboard = Keyboard()
    if r.user.ptype is PType.teacher:
        keyboard.add_line(Button('Стать студентом'))
    else:
        keyboard.add_line(Button('Стать преподом'))
    keyboard.add_line(Button('Назад'))
    return keyboard


async def settings(r: Request):
    router = Router(default=unknown_settings_command, name='settings')
    if r.user.ptype is PType.teacher:
        router.add_route(text_cond('Стать студентом'), become_student)
    else:
        router.add_route(text_cond('Стать преподом'), become_teacher)
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
