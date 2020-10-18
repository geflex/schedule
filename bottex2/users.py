from abc import abstractmethod, ABC

from bottex2.router import Condition
from bottex2.bottex import MiddlewareAggregator


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


class UserMiddleware(MiddlewareAggregator):
    async def __call__(self, **params):
        user = await _user_class.get(None, 'guest')
        print(_user_class)
        await self.handler(user=user, **params)


_user_class = TempUser
get = _user_class.get
middleware_for = UserMiddleware.deferred_add


def set_user_class(cls):
    global _user_class, get
    _user_class = cls
    get = cls.get


def state_cond(st: str) -> Condition:
    def cond(user: AbstractUser, **params) -> bool:
        return user.state == st
    return cond
