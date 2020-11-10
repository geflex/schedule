from typing import Type, List

from sqlalchemy import Column, Integer, String

from bottex2.bottex import BottexMiddleware
from bottex2.handler import Request
from bottex2.helpers.tools import Named, state_name, state_handler
from bottex2.router import Condition
from bottex2.sqlalchemy import Model


class UserModel(Model):
    __tablename__ = 'users'

    uid = Column(Integer, primary_key=True)
    platform = Column(String)
    state = Column(String)


def set_user_model(cls: Type[UserModel]):
    global user_cls
    user_cls = cls


user_cls: Type[UserModel]


class UserBottexMiddleware(BottexMiddleware):
    @staticmethod
    async def get_or_create(platform, uid):
        return await user_cls.get_or_create(platform=platform, uid=uid)

    async def get_user(self, request: Request):
        return await self.get_or_create(None, 'guest')

    async def __call__(self, request: Request):
        request.user = await self.get_user(request)
        await self.handler(request)


def state_cond(st: str) -> Condition:
    def cond(request: Request) -> bool:
        return request.user.state == st
    return cond


def gen_state_cases(handlers: List[Named]):
    routes = {}
    for obj in handlers:
        name, handler = state_name(obj), state_handler(obj)
        routes[state_cond(name)] = handler
    return routes
