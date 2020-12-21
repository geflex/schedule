from functools import cached_property

from bottex2.conditions import if_text_eq
from bottex2.ext.users import gen_state_cases
from bottex2.handler import Request, Response
from bottex2.helpers.tools import state_name
from bottex2.keyboard import Keyboard
from bottex2.router import Router
from . import inputs, models, main_logic

_ = models.i18n.gettext
_c = models.i18n.rgettext


class StartLanguageInput(inputs.BaseLanguageInput):
    state_name = 'start_setup'

    def get_lang_setter(self, lang: models.Lang):
        super_setter = super().get_lang_setter(lang)
        async def setter(r: Request):
            await super_setter(r)
            return await StartPTypeInput.switch(r)
        return setter

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        return Response(_('Выбери язык'), cls(r).keyboard)


class StartPTypeInput(inputs.PTypeInput, inputs.BaseInputChainStep):
    state_name = 'ptype_input'

    @cached_property
    def commands(self):
        commands = super().commands
        step_commands = super(inputs.PTypeInput, self).commands
        return commands + step_commands

    async def back(self, r: Request):
        return await StartLanguageInput.switch(r)

    async def set_stutent_ptype(self, r: Request):
        await super().set_stutent_ptype(r)
        return await StartGroupInput.switch(r)

    async def set_teacher_ptype(self, r: Request):
        await super().set_teacher_ptype(r)
        return await StartNameInput.switch(r)

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        return Response(_('Выбери тип профиля'), cls(r).keyboard)


class StartGroupInput(inputs.BaseGroupInput, inputs.BaseInputChainStep):
    state_name = 'start_group_input'

    @cached_property
    def commands(self):
        commands = super().commands
        step_commands = super(inputs.BaseGroupInput, self).commands
        return commands + step_commands

    async def back(self, r: Request):
        return await StartPTypeInput.switch(r)

    async def set_group(self, r: Request):
        await super().set_group(r)
        return await StartSubgroupInput.switch(r)

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        return Response(_('Введи номер группы'), cls(r).keyboard)


class StartSubgroupInput(inputs.BaseSubgroupInput, inputs.BaseInputChainStep):
    state_name = 'start_subgroup_input'

    @cached_property
    def commands(self):
        commands = super().commands
        step_commands = super(inputs.BaseSubgroupInput, self).commands
        return commands + step_commands

    async def back(self, r: Request):
        return await StartGroupInput.switch(r)

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
        return Response(_('Выбери подгруппу'), cls(r).keyboard)


class StartNameInput(inputs.BaseNameInput, inputs.BaseInputChainStep):
    state_name = 'start_name_input'

    @cached_property
    def commands(self):
        commands = super().commands
        step_commands = super(inputs.BaseNameInput, self).commands
        return commands + step_commands

    async def back(self, r: Request):
        return await StartPTypeInput.switch(r)

    async def set_name(self, r: Request):
        await super().set_name(r)
        await r.user.update(state=state_name(main_logic.Schedule))
        return end_registration_message(r)

    @classmethod
    async def switch(cls, r: Request):
        await super().switch(r)
        return Response(_('Введи имя'), cls(r).keyboard)


def end_registration_message(r: Request):
    return Response(_('Профиль настроен'), main_logic.Schedule(r).keyboard)


async def delete_me(r: Request):
    await r.user.delete()
    return Response(_('Данные успешно удалены'), Keyboard())


cases = gen_state_cases([
        StartLanguageInput,
        StartPTypeInput,
        StartGroupInput,
        StartSubgroupInput,
        StartNameInput,
])
main = Router({if_text_eq('delete me'): delete_me,  # works in any states
               **cases,
               **main_logic.cases},
              default=StartLanguageInput.switch)
