from abc import abstractmethod, ABC
from typing import Type

from bottex2.router import Condition
from bottex2.bottex import BottexHandlerMiddleware


class AbstractUser(ABC):
    @classmethod
    @abstractmethod
    async def get(cls, platform, uid) -> 'AbstractUser':
        pass

    @abstractmethod
    async def update(self, state=None):
        pass

    @property
    @abstractmethod
    def state(self):
        pass

    @property
    @abstractmethod
    def uid(self):
        pass

    @property
    @abstractmethod
    def platform(self):
        pass


class TempUser(AbstractUser):
    objects = {}

    @classmethod
    async def get(cls, platform, uid):
        if uid in cls.objects:
            return cls.objects[uid]
        obj = cls(platform, uid)
        cls.objects[uid] = obj
        return obj

    def __init__(self, platform, uid):
        self._platform = platform
        self._uid = uid
        self._state = None

    async def update(self, state=None):
        self._state = state

    @property
    def state(self):
        return self._state

    @property
    def uid(self):
        return self._uid

    @property
    def platform(self):
        return self._platform


class UserBottexHandlerMiddleware(BottexHandlerMiddleware):
    async def __call__(self, **params):
        user = await user_model.get(None, 'guest')
        await self.handler(user=user, **params)


user_model: Type[AbstractUser] = TempUser


def set_user_model(cls):
    global user_model
    user_model = cls


def state_cond(st: str) -> Condition:
    def cond(user: AbstractUser, **params) -> bool:
        return user.state == st
    return cond
