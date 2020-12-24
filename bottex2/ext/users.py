from abc import ABC, abstractmethod
from typing import Type

from bottex2.handler import Request
from bottex2.multiplatform import MultiplatformMiddleware
from bottex2.sqlalchemy import BaseModel


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


class Users:
    def __init__(self, user_cls: type):
        self.User = user_cls
        self.Middleware = type('UserMiddleware', (UserMiddleware,), {
            'user_model': self.User,
        })
