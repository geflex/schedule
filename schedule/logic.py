from bottex2.handler import Request
from bottex2.router import Router, text_cond
from bottex2.middlewares.users import state_cond
from bottex2.utils import gen_state_conds
from bottex2.views import View, Command
from bottex2.chat import Keyboard

from . import sched_logic
from . import models

ptype_kb = Keyboard([[Button('Студент'), Button('Препод')]])


async def start_setup(r: Request):
    await r.user.update(state=ptype_input.__name__)
    await r.chat.send_message('Хай! Сначала нужно кое-что настроить '
                              '(все это можно будет поменять позже в настройках)')
    await r.chat.send_message('Сначала выбери тип профиля', ptype_kb)


async def student_ptype_input(r: Request):
    await r.user.update(ptype=models.PType.student)
    await r.user.update(state=start_group_input.__name__)
    await r.chat.send_message('Окей, теперь введи номер своей группы', Keyboard())


async def teacher_ptype_input(r: Request):
    await r.user.update(ptype=models.PType.teacher)
    await r.user.update(state=start_name_input.__name__)
    await r.chat.send_message('Хорошо, теперь введите свои ФИО', Keyboard())


async def profile_type_error(r: Request):
    await r.chat.send_message('Непонятный тип профиля(\nПопробуй еще разок', ptype_kb)


ptype_input = Router({
    text_cond('студент'): student_ptype_input,
    text_cond('препод'): teacher_ptype_input,
}, default=profile_type_error, name='ptype_input')


async def start_group_input(r: Request):
    await r.user.update(group=r.text, state=sched_logic.schedule.__name__)
    await success_registration(r)


async def start_name_input(r: Request):
    await r.user.update(name=r.text, state=sched_logic.schedule.__name__)
    await success_registration(r)


async def success_registration(r: Request):
    await r.chat.send_message('Ура, все настроили', sched_logic.schedule_kb)


main = Router(gen_state_conds([
        ptype_input,
        start_group_input,
        start_name_input,
        sched_logic.schedule,
        sched_logic.settings,
        sched_logic.name_after_switching_ptype,
        sched_logic.group_after_switching_ptype,
        sched_logic.settings_name,
        sched_logic.settings_group,
        sched_logic.settings_subgroup,
     ]), default=start_setup)
