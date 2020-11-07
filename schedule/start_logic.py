from bottex2.chat import Keyboard
from bottex2.ext.i18n import Lang, _
from bottex2.ext.users import gen_state_conds
from bottex2.handler import Request
from bottex2.helpers.tools import state_name
from bottex2.router import Router, text_cond

from . import inputs
from . import sched_logic


class StartLanguageInput(inputs.BaseLanguageInput):
    name = 'start_setup'

    def get_lang_setter(self, lang: Lang):
        async def setter(r: Request):
            await r.user.update(locale=lang)
            r.chat.lang = lang
            await PTypeInput.switch(r)
        return setter

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        await r.chat.send_message(_('Выбери язык'), cls(r).keyboard)


class PTypeInput(inputs.PTypeInput):
    name = 'ptype_input'

    async def set_stutent_ptype(self, r: Request):
        await super().set_stutent_ptype(r)
        await StartGroupInput.switch(r)

    async def set_teacher_ptype(self, r: Request):
        await super().set_teacher_ptype(r)
        await StartNameInput.switch(r)

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        # await r.chat.send_message(_('Хай! Сначала нужно кое-что настроить '
        #                             '(все это можно будет поменять позже в настройках)'))
        await r.chat.send_message(_('Теперь выбери тип профиля'), cls(r).keyboard)


class StartGroupInput(inputs.BaseGroupInput):
    name = 'start_group_input'

    async def set_group(self, r: Request):
        await super().set_group(r)
        await StartSubgroupInput.switch(r)

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        await r.chat.send_message(_('Окей, теперь введи номер своей группы'), cls(r).keyboard)


class StartSubgroupInput(inputs.BaseSubgroupInput):
    name = 'start_subgroup_input'

    def get_subgroup_setter(self, subgroup_num: str):
        async def setter(r: Request):
            old_subgroup = r.user.subgroup
            await r.user.update(state=state_name(sched_logic.Schedule))
            await send_end_registration_message(r)
        return setter

    @classmethod
    async def switch(cls, r: Request):
        await r.chat.send_message(_('Выбери свою подгруппу'), cls(r).keyboard)
        await super().switch(r)


class StartNameInput(inputs.BaseNameInput):
    name = 'start_name_input'

    @classmethod
    async def switch(cls, r: Request):
        await r.chat.send_message(_('Хорошо, теперь введите свои ФИО'), cls(r).keyboard)
        await super().switch(r)
        await r.user.update(state=state_name(sched_logic.Schedule))
        await send_end_registration_message(r)


async def send_end_registration_message(r: Request):
    await r.chat.send_message(_('Ура, все настроили'), sched_logic.Schedule(r).keyboard)


async def delete_me(r: Request):
    await r.user.delete()
    await r.chat.send_message(_('Данные успешно удалены'), Keyboard())


conds = gen_state_conds([
        StartLanguageInput,
        PTypeInput,
        StartGroupInput,
        StartSubgroupInput,
        StartNameInput,
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
               **conds},
              default=StartLanguageInput.switch)
