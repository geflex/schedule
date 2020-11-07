import re
from functools import cached_property
from typing import List

from bottex2.ext.i18n import _, Lang
from bottex2.handler import Request
from bottex2.helpers import regexp
from bottex2.router import Router, regexp_cond
from bottex2.views import View, Command
from .models import PType


class PTypeInput(View):
    @property
    def commands(self) -> List[List[Command]]:
        return [[
            Command(_('Студент'), self.set_stutent_ptype),
            Command(_('Препод'), self.set_teacher_ptype),
        ]]

    async def set_stutent_ptype(self, r: Request):
        await self.r.user.update(ptype=PType.student)

    async def set_teacher_ptype(self, r: Request):
        await self.r.user.update(ptype=PType.teacher)

    async def default(self, r: Request):
        await r.chat.send_message(_('Неизвестный тип профиля'), self.keyboard)


class LanguageInput(View):
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


class SubgroupInput(View):
    @property
    def commands(self):
        commands = [[
            Command(_('Первая'), self.get_subgroup_setter('1')),
            Command(_('Вторая'), self.get_subgroup_setter('2')),
        ]]
        return commands

    def get_subgroup_setter(self, subgroup_num: str):
        async def setter(r: Request):
            await r.user.update(subgroup=subgroup_num)
        return setter

    async def default(self, r: Request):
        await r.chat.send_message(_('Такой подгруппы не существует'))


class GroupInput(View):
    exp = re.compile(r'\d{8}')
    revexp = regexp.compile(exp)

    @property
    def commands(self):
        return []

    @cached_property
    def router(self) -> Router:
        router = super().router
        router.add_route(regexp_cond(self.exp), self.set_group)
        return router

    async def set_group(self, r: Request):
        await r.user.update(group=r.text)

    async def default(self, r: Request):
        await r.chat.send_message(_('Номер группы должен состоять из 8 цифр'), self.keyboard)


class NameInput(View):
    @property
    def commands(self):
        return []

    async def set_name(self, r: Request):
        await r.user.update(name=r.text)

    async def default(self, r: Request):
        await self.set_name(r)
