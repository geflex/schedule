import re
from abc import ABC, abstractmethod
from functools import cached_property
from typing import List, Awaitable

from sqlalchemy.orm.exc import NoResultFound

from bottex2.conditions import if_re_match
from bottex2.handler import Request, Response, ErrorResponse, TResponse
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

    @staticmethod
    async def set_stutent_ptype(r: Request):
        await r.user.update(ptype=models.PType['student'])

    @staticmethod
    async def set_teacher_ptype(r: Request):
        await r.user.update(ptype=models.PType['teacher'])

    async def default(self, r: Request):
        return Response(_('Неизвестный тип профиля'))


class BaseLanguageInput(View):
    @property
    def commands(self):
        commands = [
            [Command(lang.name, self.get_lang_setter(lang))]
            for lang in models.i18n.Lang
        ]
        return commands

    @staticmethod
    def get_lang_setter(lang: models.Lang):
        async def setter(r: Request):
            await r.user.update(locale=lang)
        return setter

    async def default(self, r: Request):
        return Response(_('Выбранный язык не поддерживается'))


class BaseSubgroupInput(View):
    @property
    def commands(self):
        commands = [[
            Command(_c(sg.name), self.get_subgroup_setter(sg))
            for sg in models.Subgroup
        ]]
        return commands

    @staticmethod
    def get_subgroup_setter(subgroup: models.Subgroup):
        async def setter(r: Request):
            await r.user.update(subgroup=subgroup)
        return setter

    async def default(self, r: Request):
        return Response(_('Такой подгруппы не существует'))


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

    @staticmethod
    async def set_group(r: Request):
        try:
            group = models.Group.query.filter(models.Group.name == r.text).one()
        except NoResultFound:
            raise ErrorResponse(Response(_('Такой группы не существует')))
        else:
            await r.user.update(group=group)

    async def default(self, r: Request):
        return Response(_('Номер группы должен состоять из 8 цифр'))


class BaseNameInput(View):
    @property
    def commands(self) -> List[List[Command]]:
        return []

    @staticmethod
    async def set_name(r: Request):
        await r.user.update(name=r.text)

    def default(self, r: Request):
        return self.set_name(r)


class InputChainStep(View, ABC):
    @property
    def commands(self) -> List[List[Command]]:
        return [[Command(_c('Назад'), self.back)]]

    @staticmethod
    @abstractmethod
    def back(r: Request) -> Awaitable[TResponse]:
        pass
