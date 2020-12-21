from abc import ABC, abstractmethod
from typing import Type, Iterable

from sqlalchemy import Column, Integer, String

from bottex2.handler import Request
from bottex2.helpers.tools import state_name, state_handler
from bottex2.multiplatform import MultiplatformMiddleware
from bottex2.router import TCondition
from bottex2.sqlalchemy import BaseModel, SQLAlchemy


class BaseUserMixin:
    __tablename__ = 'users'

    uid = Column(Integer, primary_key=True)
    platform = Column(String)
    state = Column(String)


class UserMiddleware(MultiplatformMiddleware, ABC):
    user_model: Type[BaseModel]

    @classmethod
    async def get_or_create(cls, platform, uid):
        user = cls.user_model.get_or_create(platform=platform, uid=uid)
        cls.user_model.session.commit()
        return user

    @abstractmethod
    async def get_user(self, request: Request):
        # return await self.get_or_create
        return

    async def __call__(self, request: Request):
        request.user = await self.get_user(request)
        return await super().__call__(request)


def state_cond(st: str) -> TCondition:
    def cond(request: Request) -> bool:
        return request.user.state == st
    return cond


def gen_state_cases(handlers: Iterable):
    routes = {}
    for obj in handlers:
        name, handler = state_name(obj), state_handler(obj)
        routes[state_cond(name)] = handler
    return routes


class Users:
    def __init__(self, db: SQLAlchemy, user_mixin=object):
        self.User = type('User', (db.Model, BaseUserMixin, user_mixin), {})
        self.Middleware = type('UserMiddleware', (UserMiddleware,), {
            'user_model': self.User,
        })
