from functools import cached_property, partial

from bottex2.chat import Keyboard
from bottex2.ext.i18n import gettext
from bottex2.ext.users import gen_state_cases
from bottex2.handler import Request
from bottex2.helpers.tools import state_name
from bottex2.router import Router, if_text
from . import inputs
from . import main_logic
from .models import Lang

_ = partial(gettext, domain='schedule')


class StartLanguageInput(inputs.BaseLanguageInput):
    name = 'start_setup'

    def get_lang_setter(self, lang: Lang):
        super_setter = super().get_lang_setter(lang)
        async def setter(r: Request):
            await super_setter(r)
            await PTypeInput.switch(r)
        return setter

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        return r.resp(_('Выбери язык'), cls(r).keyboard)


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
        return r.resp(_('Теперь выбери тип профиля'), cls(r).keyboard)


class StartGroupInput(inputs.BaseGroupInput):
    name = 'start_group_input'

    @cached_property
    def commands(self):
        # return [[Command(_c('Я не знаю номер группы'), )]]
        return []

    async def set_group(self, r: Request):
        await super().set_group(r)
        await StartSubgroupInput.switch(r)

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        return r.resp(_('Окей, теперь введи номер своей группы'), cls(r).keyboard)


class StartSubgroupInput(inputs.BaseSubgroupInput):
    name = 'start_subgroup_input'

    def get_subgroup_setter(self, subgroup_num: str):
        super_setter = super().get_subgroup_setter(subgroup_num)
        async def setter(r: Request):
            old_subgroup = r.user.subgroup
            await super_setter(r)
            await r.user.update(state=state_name(main_logic.Schedule))
            return end_registration_message(r)
        return setter

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        return r.resp(_('Выбери свою подгруппу'), cls(r).keyboard)


class StartNameInput(inputs.BaseNameInput):
    name = 'start_name_input'

    @cached_property
    def commands(self):
        return []

    async def set_name(self, r: Request):
        await super().set_name(r)
        await r.user.update(state=state_name(main_logic.Schedule))
        return end_registration_message(r)

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        return r.resp(_('Хорошо, теперь введите свои ФИО'), cls(r).keyboard)


def end_registration_message(r: Request):
    return r.resp(_('Ура, все настроили'), main_logic.Schedule(r).keyboard)


async def delete_me(r: Request):
    await r.user.delete()
    return r.resp(_('Данные успешно удалены'), Keyboard())


cases = gen_state_cases([
        StartLanguageInput,
        PTypeInput,
        StartGroupInput,
        StartSubgroupInput,
        StartNameInput,
])
main = Router({if_text('delete me'): delete_me,  # works in any states
               **cases,
               **main_logic.cases},
              default=StartLanguageInput.switch)
