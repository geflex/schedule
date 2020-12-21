import re
from abc import ABC, abstractmethod
from functools import cached_property
from typing import List

from sqlalchemy.orm.exc import NoResultFound

from bottex2.conditions import if_re_match
from bottex2.handler import Request, Response, ErrorResponse
from bottex2.helpers import regexp
from bottex2.router import Router
from bottex2.views import View, Command
from . import models

_ = models.i18n.gettext
_c = models.i18n.rgettext


class PTypeInput(View):
    @property
    def commands(self) -> List[List[Command]]:
        return [[
            Command(_c('Студент'), self.set_stutent_ptype),
            Command(_c('Препод'), self.set_teacher_ptype),
        ]]

    async def set_stutent_ptype(self, r: Request):
        await self.r.user.update(ptype=models.PTypeEnum.student)

    async def set_teacher_ptype(self, r: Request):
        await self.r.user.update(ptype=models.PTypeEnum.teacher)

    async def default(self, r: Request):
        return Response(_('Неизвестный тип профиля'), self.keyboard)


class BaseLanguageInput(View):
    @property
    def commands(self):
        commands = [
            [Command(lang.name, self.get_lang_setter(lang))]
            for lang in models.i18n.Lang
        ]
        return commands

    def get_lang_setter(self, lang: models.Lang):
        async def setter(r: Request):
            await r.user.update(locale=lang)
        return setter

    async def default(self, r: Request):
        return Response(_('Выбранный язык не поддерживается'), self.keyboard)


class BaseSubgroupInput(View):
    @property
    def commands(self):
        commands = [[
            Command(_c(sg.name), self.get_subgroup_setter(sg))
            for sg in models.Subgroup
        ]]
        return commands

    def get_subgroup_setter(self, subgroup: models.Subgroup):
        async def setter(r: Request):
            await r.user.update(subgroup=subgroup)
        return setter

    async def default(self, r: Request):
        return Response(_('Такой подгруппы не существует'), self.keyboard)


class BaseGroupInput(View):
    exp = re.compile(r'\d{8}')
    revexp = regexp.compile(exp)

    @property
    def commands(self) -> List[List[Command]]:
        return []

    @cached_property
    def router(self) -> Router:
        router = super().router
        router[if_re_match(self.exp)] = self.set_group
        return router

    async def set_group(self, r: Request):
        try:
            group = models.Group.query.filter(models.Group.name == r.text).one()
        except NoResultFound:
            raise ErrorResponse(Response(_('Такой группы не существует'), self.keyboard))
        else:
            await r.user.update(group=group)

    async def default(self, r: Request):
        return Response(_('Номер группы должен состоять из 8 цифр'), self.keyboard)


class BaseNameInput(View):
    @property
    def commands(self) -> List[List[Command]]:
        return []

    async def set_name(self, r: Request):
        await r.user.update(name=r.text)

    def default(self, r: Request):
        return self.set_name(r)


class BaseInputChainStep(View, ABC):
    @property
    def commands(self) -> List[List[Command]]:
        return [[Command(_c('Назад'), self.back)]]

    @abstractmethod
    async def back(self, r: Request):
        pass
