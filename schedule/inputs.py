import re
from abc import ABC
from functools import cached_property, partial
from typing import List

from bottex2.ext.i18n import gettext
from bottex2.handler import Request
from bottex2.helpers import regexp
from bottex2.router import Router, if_regexp
from bottex2.views import View, Command
from .models import PType, Lang

_ = partial(gettext, domain='schedule')
_c = partial(gettext, domain='reversible')


class PTypeInput(View):
    @property
    def commands(self) -> List[List[Command]]:
        return [[
            Command(_c('Студент'), self.set_stutent_ptype),
            Command(_c('Препод'), self.set_teacher_ptype),
        ]]

    async def set_stutent_ptype(self, r: Request):
        await self.r.user.update(ptype=PType.student)

    async def set_teacher_ptype(self, r: Request):
        await self.r.user.update(ptype=PType.teacher)

    async def default(self, r: Request):
        await r.chat.send_message(_('Неизвестный тип профиля'), self.keyboard)


class BaseLanguageInput(View):
    @property
    def commands(self):
        commands = [
            [Command(lang.value, self.get_lang_setter(lang))]
            for lang in Lang
        ]
        return commands

    def get_lang_setter(self, lang: Lang):
        async def setter(r: Request):
            await r.user.update(locale=lang)
            r.chat.lang = lang  # !!! BAD
        return setter

    async def default(self, r: Request):
        await r.chat.send_message(_('Выбранный язык не поддерживается'), self.keyboard)


class BaseSubgroupInput(View):
    @property
    def commands(self):
        commands = [[
            Command(_c('Первая'), self.get_subgroup_setter('1')),
            Command(_c('Вторая'), self.get_subgroup_setter('2')),
        ]]
        return commands

    def get_subgroup_setter(self, subgroup_num: str):
        async def setter(r: Request):
            await r.user.update(subgroup=subgroup_num)
        return setter

    async def default(self, r: Request):
        await r.chat.send_message(_('Такой подгруппы не существует'))


class BaseGroupInput(View, ABC):
    exp = re.compile(r'\d{8}')
    revexp = regexp.compile(exp)

    @cached_property
    def router(self) -> Router:
        router = super().router
        router.add_route(if_regexp(self.exp), self.set_group)
        return router

    async def set_group(self, r: Request):
        await r.user.update(group=r.text)

    async def default(self, r: Request):
        await r.chat.send_message(_('Номер группы должен состоять из 8 цифр'), self.keyboard)


class BaseNameInput(View, ABC):

    async def set_name(self, r: Request):
        await r.user.update(name=r.text)

    async def default(self, r: Request):
        await self.set_name(r)
