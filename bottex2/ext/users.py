from typing import Type

from sqlalchemy import Column, Integer, String

from bottex2.bottex import BottexMiddleware
from bottex2.handler import Request
from bottex2.helpers.tools import state_name, state_handler
from bottex2.router import Condition
from bottex2.sqlalchemy import Model


class UserModel(Model):
    __tablename__ = 'users'

    uid = Column(Integer, primary_key=True)
    platform = Column(String)
    state = Column(String)


class UserBottexMiddleware(BottexMiddleware):
    user_model: Type[UserModel]

    @classmethod
    async def get_or_create(cls, platform, uid):
        user = cls.user_model.get_or_create(platform=platform, uid=uid)
        cls.user_model.session.commit()
        return user

    async def get_user(self, request: Request):
        # return await self.get_or_create
        return

    async def __call__(self, request: Request):
        request.user = await self.get_user(request)
        return await self.handler(request)


def user_middleware(user_model: Type[UserModel]):
    return type('UserBottexMiddleware', (UserBottexMiddleware, ), {
        'user_model': user_model,
    })


def state_cond(st: str) -> Condition:
    def cond(request: Request) -> bool:
        return request.user.state == st
    return cond


def gen_state_cases(handlers):
    routes = {}
    for obj in handlers:
        name, handler = state_name(obj), state_handler(obj)
        routes[state_cond(name)] = handler
    return routes
