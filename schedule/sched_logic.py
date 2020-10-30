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


def get_settings_kb(r: Request):
    keyboard = Keyboard([])
    if r.user.ptype is PType.teacher:
        keyboard.add_line(Button('Стать студентом'))
    else:
        keyboard.add_line(Button('Стать преподом'))
    keyboard.add_line(Button('Назад'))
    return keyboard


unknown_command_str = 'Хм непонятная команда'


async def unknown_command(r: Request):
    await r.chat.send_message(unknown_command_str, schedule_kb)


async def unknown_settings_command(r: Request):
    await r.chat.send_message(unknown_command_str, get_settings_kb(r))


async def today(r: Request):
    await r.chat.send_message(f'Так расписание для {r.user.group} на {Date.today()}', schedule_kb)


async def tomorrow(r: Request):
    await r.chat.send_message(f'Так расписание для {r.user.group} на {Date.tomorrow()}', schedule_kb)


async def back(r: Request):
    await r.chat.send_message('Главное меню', schedule_kb)
    await r.user.update(state=schedule.__name__)


settings = Router({
    text_cond('назад'): back,
}, default=unknown_settings_command, name='settings')


async def switch_to_settings(r: Request):
    await r.chat.send_message('Настройки', get_settings_kb(r))
    await r.user.update(state=settings.__name__)


schedule = Router({
    text_cond('сегодня'): today,
    text_cond('завтра'): tomorrow,
    text_cond('настройки'): switch_to_settings,
}, default=unknown_command, name='schedule')
