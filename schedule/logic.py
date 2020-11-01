from functools import cached_property
from typing import List

from bottex2.handler import Request
from bottex2.router import Router, text_cond
from bottex2.middlewares.users import state_cond
from bottex2.utils import gen_state_conds
from bottex2.views import View, Command
from bottex2.chat import Keyboard

from . import sched_logic
from . import models


async def start_setup(r: Request):
    await r.user.update(state=PTypeInput.name)
    await r.chat.send_message('Хай! Сначала нужно кое-что настроить '
                              '(все это можно будет поменять позже в настройках)')
    await r.chat.send_message('Сначала выбери тип профиля', PTypeInput(r).keyboard)


async def student_ptype_input(r: Request):
    await r.user.update(ptype=models.PType.student, state=start_group_input.__name__)
    await r.chat.send_message('Окей, теперь введи номер своей группы', Keyboard())


async def teacher_ptype_input(r: Request):
    await r.user.update(state=start_name_input.__name__, ptype=models.PType.teacher)
    await r.chat.send_message('Хорошо, теперь введите свои ФИО', Keyboard())


class PTypeInput(View):
    name = 'ptype_input'

    @cached_property
    def commands(self) -> List[List[Command]]:
        return [
            [
                Command('Студент', student_ptype_input),
                Command('Препод', teacher_ptype_input)
            ]
        ]

    async def default(self, r: Request):
        await r.chat.send_message('Непонятный тип профиля', self.keyboard)


async def start_group_input(r: Request):
    await r.user.update(group=r.text, state=sched_logic.schedule.__name__)
    await success_registration(r)


async def start_name_input(r: Request):
    await r.user.update(name=r.text, state=sched_logic.schedule.__name__)
    await success_registration(r)


async def success_registration(r: Request):
    await r.chat.send_message('Ура, все настроили', sched_logic.schedule_kb)


async def delete_me(r: Request):
    await r.user.delete()
    await r.chat.send_message('Данные успешно удалены', Keyboard())


conds = gen_state_conds([
        PTypeInput,
        start_group_input,
        start_name_input,
        sched_logic.schedule,
        sched_logic.Settings,
        sched_logic.name_after_switching_ptype,
        sched_logic.group_after_switching_ptype,
        sched_logic.settings_name,
        sched_logic.settings_group,
        sched_logic.settings_subgroup,
])
main = Router({text_cond('delete me'): delete_me,  # works in any state
               state_cond(PTypeInput.name): PTypeInput.handle,
               **conds},
              default=start_setup)
