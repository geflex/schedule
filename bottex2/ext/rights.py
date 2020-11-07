from enum import Enum

from bottex2.handler import Request
from bottex2.router import Condition


class RightsUserMixin:
    rights: Enum


def if_user_can(permission: Enum) -> Condition:
    def case(r: Request):
        return permission in r.user.rights
    return case
