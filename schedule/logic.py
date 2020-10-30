from bottex2.handler import Request
from bottex2.router import Router, text_cond
from bottex2.middlewares.users import gen_conds
from bottex2.chat import Keyboard, Button

from schedule import models
from .schedule_logic import schedule


empty_kb = Keyboard([])
ptype_kb = Keyboard([[Button('Студент'), Button('Препод')]])


async def init_user(r: Request):
    await r.user.update(state=ptype_input.__name__)
    await r.chat.send_message('Привет! Сначала нужно кое-что настроить '
                              '(все это можно будет поменять позже в настройках)')
    await r.chat.send_message('Сначала выбери тип профиля', kb=ptype_kb)


async def student_ptype_input(r: Request):
    await r.user.update(ptype=models.PType.student)
    await r.user.update(state=group_input.__name__)
    await r.chat.send_message('Окей, теперь введи номер своей группы', kb=empty_kb)


async def teacher_ptype_input(r: Request):
    await r.user.update(ptype=models.PType.teacher)
    await r.user.update(state=fio_input.__name__)
    await r.chat.send_message('Хорошо, теперь введите свои ФИО', empty_kb)


async def profile_type_error(r: Request):
    await r.chat.send_message('Непонятный тип профиля(\nПопробуй еще разок', kb=ptype_kb)


ptype_input = Router({
    text_cond('студент'): student_ptype_input,
    text_cond('препод'): teacher_ptype_input,
}, default=profile_type_error, name='ptype_input')


async def group_input(r: Request):
    await r.user.update(group=r.text, state=schedule.__name__)
    await success_registration(r)


async def fio_input(r: Request):
    await r.user.update(fio=r.text, state=schedule.__name__)
    await success_registration(r)


async def success_registration(r: Request):
    await r.chat.send_message('Ура, все настроили')


main = Router(gen_conds([
        ptype_input,
        group_input,
        fio_input,
        schedule,
     ]), default=init_user)
