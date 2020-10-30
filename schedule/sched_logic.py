from bottex2.chat import Button, Keyboard
from bottex2.router import Router, text_cond
from bottex2.handler import Request


schedule_kb = Keyboard([
    [Button('Сегодня')],
    [Button('Завтра')],
    [Button('Настройки')],
])


settings_kb = Keyboard([
    [Button('Назад')],
])


async def unknown_command(r: Request):
    await r.chat.send_message('Хм непонятная команда', schedule_kb)


async def unknown_settings_command(r: Request):
    await r.chat.send_message('Хм непонятная команда', settings_kb)


async def today(r: Request):
    await r.chat.send_message(f'Такс расписание для {r.user.group}', schedule_kb)


async def tomorrow(r: Request):
    await r.chat.send_message(f'Такс расписание для {r.user.group}', schedule_kb)


async def back(r: Request):
    await r.chat.send_message('Переходим в главное меню', schedule_kb)
    await r.user.update(state=schedule.__name__)


settings = Router({
    text_cond('назад'): back,
}, default=unknown_command, name='settings')


async def go_to_settings(r: Request):
    await r.chat.send_message('Переходим в настройки', settings_kb)
    await r.user.update(state=settings.__name__)


schedule = Router({
    text_cond('сегодня'): today,
    text_cond('завтра'): tomorrow,
    text_cond('настройки'): go_to_settings,
}, default=unknown_command, name='schedule')
