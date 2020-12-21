from enum import Enum
from typing import Type

import sqlalchemy as sa

from bottex2.handler import Request
from bottex2.router import TCondition


class RightsUserMixin:
    rights: Enum


def if_user_can(permission: Enum) -> TCondition:
    def case(r: Request):
        return permission in r.user.rights
    return case


class Rights:
    def __init__(self, enum: Type[Enum]):
        self.UserMixin = type('RightsUserMixin', (RightsUserMixin, ), {
            'rights': sa.Column(sa.types.Enum(enum))
        })
