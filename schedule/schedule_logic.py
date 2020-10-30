from bottex2.router import Router, text_cond
from bottex2.handler import Request


async def schedule_main(r: Request):
    await r.chat.send_message('упс пака')


async def today(r: Request):
    await r.chat.send_message('Такс расписание на сегодня')


async def tomorrow(r: Request):
    await r.chat.send_message('Такс расписание на завтра')


async def back(r: Request):
    await r.chat.send_message('Переходим в главное меню')
    await r.user.update(state=schedule.__name__)


settings = Router({
    text_cond('назад'): back,
}, name='settings')


schedule = Router({
    text_cond('сегодня'): today,
    text_cond('завтра'): tomorrow,
    text_cond('настройки'): settings,
}, default=schedule_main, name='schedule')
