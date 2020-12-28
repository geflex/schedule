from typing import Awaitable

from bottex2.conditions import if_text_eq
from bottex2.handler import Request, Response, TResponse
from bottex2.keyboard import Keyboard
from bottex2.router import Router
from bottex2.states import gen_state_cases
from . import inputs, models, main_logic

_ = models.i18n.gettext
_c = models.i18n.rgettext


class StartLanguageInput(inputs.BaseLanguageInput):
    state_name = 'start_setup'

    @classmethod
    def get_lang_setter(cls, lang: models.Lang):
        super_setter = super().get_lang_setter(lang)
        async def setter(r: Request):
            await super_setter(r)
            return await StartPTypeInput.switcher(r)
        return setter

    async def switch(self):
        await super().switch()
        return Response(_('Выбери язык'))


class StartPTypeInput(inputs.PTypeInput, inputs.InputChainStep):
    state_name = 'ptype_input'

    @property
    def commands(self):
        commands = super().commands
        step_commands = super(inputs.PTypeInput, self).commands
        return commands + step_commands

    @staticmethod
    def back(r: Request) -> Awaitable[TResponse]:
        return StartLanguageInput.switcher(r)

    @classmethod
    async def set_stutent_ptype(cls, r: Request):
        await super().set_stutent_ptype(r)
        return await StartGroupInput.switcher(r)

    @classmethod
    async def set_teacher_ptype(cls, r: Request):
        await super().set_teacher_ptype(r)
        return await StartNameInput.switcher(r)

    async def switch(self):
        await super().switch()
        return Response(_('Выбери тип профиля'))


class StartGroupInput(inputs.BaseGroupInput, inputs.InputChainStep):
    state_name = 'start_group_input'

    @property
    def commands(self):
        commands = super().commands
        step_commands = super(inputs.BaseGroupInput, self).commands
        return commands + step_commands

    @staticmethod
    def back(r: Request):
        return StartPTypeInput.switcher(r)

    @classmethod
    async def set_group(cls, r: Request):
        await super().set_group(r)
        return await StartSubgroupInput.switcher(r)

    async def switch(self):
        await super().switch()
        return Response(_('Введи номер группы'))


class StartSubgroupInput(inputs.BaseSubgroupInput, inputs.InputChainStep):
    state_name = 'start_subgroup_input'

    @property
    def commands(self):
        commands = super().commands
        step_commands = super(inputs.BaseSubgroupInput, self).commands
        return commands + step_commands

    @staticmethod
    def back(r: Request):
        return StartGroupInput.switcher(r)

    @classmethod
    def get_subgroup_setter(cls, subgroup: models.Subgroup):
        super_setter = super().get_subgroup_setter(subgroup)
        async def setter(r: Request):
            await super_setter(r)
            await r.user.set_state(main_logic.Schedule)
            return end_registration_message(r)
        return setter

    async def switch(self):
        await super().switch()
        return Response(_('Выбери подгруппу'))


class StartNameInput(inputs.BaseNameInput, inputs.InputChainStep):
    state_name = 'start_name_input'

    @property
    def commands(self):
        commands = super().commands
        step_commands = super(inputs.BaseNameInput, self).commands
        return commands + step_commands

    @staticmethod
    def back(r: Request):
        return StartPTypeInput.switcher(r)

    @classmethod
    async def set_name(cls, r: Request):
        await super().set_name(r)
        await r.user.set_state(main_logic.Schedule)
        return end_registration_message(r)

    async def switch(self):
        await super().switch()
        return Response(_('Введи имя'))


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
              default=StartLanguageInput.switcher)
