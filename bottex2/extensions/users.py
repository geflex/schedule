from typing import Type, List

from sqlalchemy import Column, Integer, String

from bottex2.helpers.tools import Named, name
from bottex2.sqlalchemy import Base
from bottex2.handler import Request
from bottex2.router import Condition
from bottex2.bottex import BottexHandlerMiddleware
from bottex2.views import View


class UserModel(Base):
    __tablename__ = 'users'

    uid = Column(Integer, primary_key=True)
    platform = Column(String)
    state = Column(String)


def set_user_model(cls: Type[UserModel]):
    global user_cls
    user_cls = cls


user_cls: Type[UserModel]


class UserBottexHandlerMiddleware(BottexHandlerMiddleware):
    @staticmethod
    async def get_or_create(**kwargs):
        return await user_cls.get_or_create(**kwargs)

    async def get_user(self, request: Request):
        return await self.get_or_create(platform=None, uid='guest')

    async def __call__(self, request: Request):
        request.user = await self.get_user(request)
        await self.handler(request)


def state_cond(st: str) -> Condition:
    def cond(request: Request) -> bool:
        return request.user.state == st
    return cond


def gen_state_conds(handlers: List[Named]):
    routes = {}
    for obj in handlers:
        if isinstance(obj, type) and issubclass(obj, View):
            handler = obj.handle
        else:
            handler = obj
        routes[state_cond(name(obj))] = handler
    return routes
