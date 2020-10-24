from bottex2.handler import request_handler, Request
from bottex2.router import Router, text_cond
from bottex2.middlewares.users import gen_conds
from schedule import models


@request_handler
async def init_user(request: Request):
    await request.user.update(state=hello.__name__)
    await request.chat.send_message('user was initialised')


@request_handler
async def hello(r: Request):
    await r.user.update(state=ptype_input.__name__)
    await r.chat.send_message('Привет! Чтобы все заработало, сначала нужно кое-что настроить '
                              '(все это можно будет поменять позже в настройках)')


@request_handler
async def student_ptype_input(r: Request):
    await r.user.update(ptype=models.PType.student)
    await r.user.update(state=group_input.__name__)
    await r.chat.send_message('Окей, теперь введи номер своей группы')


@request_handler
async def teacher_ptype_input(r: Request):
    await r.user.update(ptype=models.PType.teacher)
    await r.user.update(state=fio_input.__name__)
    await r.chat.send_message('Хорошо, теперь введите свои ФИО')


@request_handler
async def profile_type_error(r: Request):
    await r.chat.send_message('Непонятный тип профиля(\nПопробуй еще разок')


ptype_input = Router({
    text_cond('студент'): student_ptype_input,
    text_cond('препод'): teacher_ptype_input,
}, default=profile_type_error, name='ptype_input')


@request_handler
async def group_input(r: Request):
    await r.user.update(group=r.text, state=schedule.__name__)
    await r.chat.send_message('Ура, все настроили')


@request_handler
async def fio_input(r: Request):
    await r.user.update(fio=r.text, state=schedule.__name__)
    await r.chat.send_message('Ура, все настроили')


@request_handler
async def schedule_main(r: Request):
    await r.chat.send_message('упс пака')
    await r.user.update(state=None)


schedule = Router({}, default=schedule_main)


main = Router(gen_conds([
        ptype_input,
        group_input,
        fio_input,
        schedule,
     ]), default=init_user)
