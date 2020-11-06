from functools import cached_property
from typing import List

from bottex2.chat import Keyboard
from bottex2.ext.i18n import Lang
from bottex2.ext.users import state_cond, gen_state_conds
from bottex2.handler import Request
from bottex2.helpers.tools import state_name
from bottex2.router import Router, text_cond
from bottex2.views import View, Command
from . import models
from . import sched_logic

_ = lambda s: s


class StartLanguageInput(sched_logic.SettingsLanguageInput):
    name = 'start_setup'

    def get_lang_setter(self, lang: Lang):
        async def setter(r: Request):
            await r.user.update(locale=lang)
            r.chat.lang = lang
            await PTypeInput.switch(r)
        return setter

    @classmethod
    async def switch(cls, r: Request):
        await super(sched_logic.BaseSettingsInput, cls).switch(r)
        await r.chat.send_message(_('Выбери язык'), cls(r).keyboard)


async def student_ptype_input(r: Request):
    await r.user.update(ptype=models.PType.student, state=state_name(start_group_input))
    await r.chat.send_message(_('Окей, теперь введи номер своей группы'), Keyboard())


async def teacher_ptype_input(r: Request):
    await r.user.update(state=state_name(start_name_input), ptype=models.PType.teacher)
    await r.chat.send_message(_('Хорошо, теперь введите свои ФИО'), Keyboard())


class PTypeInput(View):
    name = 'ptype_input'

    @cached_property
    def commands(self) -> List[List[Command]]:
        return [[
            Command(_('Студент'), student_ptype_input),
            Command(_('Препод'), teacher_ptype_input),
        ]]

    async def default(self, r: Request):
        await r.chat.send_message(_('Непонятный тип профиля'), self.keyboard)

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        # await r.chat.send_message(_('Хай! Сначала нужно кое-что настроить '
        #                             '(все это можно будет поменять позже в настройках)'))
        await r.chat.send_message(_('Теперь выбери тип профиля'), cls(r).keyboard)


async def start_group_input(r: Request):
    await r.user.update(group=r.text)
    await StartSubgroupInput.switch(r)


class StartSubgroupInput(sched_logic.SettingsSubgroupInput):
    name = 'start_subgroup_input'

    def get_subgroup_setter(self, subgroup_num: str):
        async def subgroup_setter(r: Request):
            old_subgroup = r.user.subgroup
            await r.user.update(subgroup=subgroup_num, state=state_name(sched_logic.Schedule))
            await send_end_registration_message(r)
        return subgroup_setter

    @classmethod
    async def switch(cls, r: Request):
        await r.chat.send_message(_('Выбери свою подгруппу'), cls(r).keyboard)
        await super(sched_logic.SettingsSubgroupInput, cls).switch(r)


async def start_name_input(r: Request):
    await r.user.update(name=r.text, state=state_name(sched_logic.Schedule))
    await send_end_registration_message(r)


async def send_end_registration_message(r: Request):
    await r.chat.send_message(_('Ура, все настроили'), sched_logic.Schedule(r).keyboard)


async def delete_me(r: Request):
    await r.user.delete()
    await r.chat.send_message(_('Данные успешно удалены'), Keyboard())


conds = gen_state_conds([
        StartLanguageInput,
        PTypeInput,
        start_group_input,
        StartSubgroupInput,
        start_name_input,
        sched_logic.Schedule,
        sched_logic.Settings,
        sched_logic.name_after_switching_ptype,
        sched_logic.group_after_switching_ptype,
        sched_logic.SettingsLanguageInput,
        sched_logic.SettingsNameInput,
        sched_logic.SettingsGroupInput,
        sched_logic.SettingsSubgroupInput,
])
main = Router({text_cond('delete me'): delete_me,  # works in any states
               state_cond(state_name(PTypeInput)): PTypeInput.handle,
               **conds},
              default=StartLanguageInput.switch)
