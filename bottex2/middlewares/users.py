from typing import List
from types import FunctionType

from sqlalchemy import Column, Integer, String

from bottex2.sqlalchemy import Base
from bottex2.handler import Request
from bottex2.router import Condition
from bottex2.bottex import BottexHandlerMiddleware


class UserBottexHandlerMiddleware(BottexHandlerMiddleware):
    async def __call__(self, request: Request):
        request.user = await UserModel.get(None, 'guest')
        await self.handler(request)


def state_cond(st: str) -> Condition:
    def cond(request: Request) -> bool:
        return request.user.state == st
    return cond


def gen_state_conds(routes: List[FunctionType]):
    return {state_cond(func.__name__): func for func in routes}


class UserModel(Base):
    __tablename__ = 'users'

    uid = Column(Integer, primary_key=True)
    platform = Column(String)
    state = Column(String)
