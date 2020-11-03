from functools import cached_property
from typing import List

from bottex2.handler import Request
from bottex2.router import Router, text_cond
from bottex2.extensions.users import state_cond
from bottex2.utils import gen_state_conds, name
from bottex2.views import View, Command
from bottex2.chat import Keyboard

from . import sched_logic
from . import models


async def start_setup(r: Request):
    await r.user.update(state=name(PTypeInput))
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
        return [[
                Command('Студент', student_ptype_input),
                Command('Препод', teacher_ptype_input),
        ]]

    async def default(self, r: Request):
        await r.chat.send_message('Непонятный тип профиля', self.keyboard)


async def start_group_input(r: Request):
    await r.user.update(group=r.text)
    await StartSubgroupInput.switch(r)


class StartSubgroupInput(sched_logic.SettingsSubgroup):
    name = 'start_subgroup_input'

    def get_subgroup_setter(self, subgroup_num: str):
        async def subgroup_setter(r: Request):
            old_subgroup = r.user.subgroup
            await r.user.update(subgroup=subgroup_num, state=name(sched_logic.Schedule))
            await send_end_registratioon_message(r)
        return subgroup_setter

    @classmethod
    async def switch(cls, r: Request):
        await r.chat.send_message('Выбери свою подгруппу', cls(r).keyboard)
        await super(sched_logic.SettingsSubgroup, cls).switch(r)


async def start_name_input(r: Request):
    await r.user.update(name=r.text, state=name(sched_logic.Schedule))
    await send_end_registratioon_message(r)


async def send_end_registratioon_message(r: Request):
    await r.chat.send_message('Ура, все настроили', sched_logic.Schedule(r).keyboard)


async def delete_me(r: Request):
    await r.user.delete()
    await r.chat.send_message('Данные успешно удалены', Keyboard())


conds = gen_state_conds([
        PTypeInput,
        start_group_input,
        StartSubgroupInput,
        start_name_input,
        sched_logic.Schedule,
        sched_logic.Settings,
        sched_logic.name_after_switching_ptype,
        sched_logic.group_after_switching_ptype,
        sched_logic.SettingsName,
        sched_logic.SettingsGroup,
        sched_logic.SettingsSubgroup,
])
main = Router({text_cond('delete me'): delete_me,  # works in any state
               state_cond(name(PTypeInput)): PTypeInput.handle,
               **conds},
              default=start_setup)
