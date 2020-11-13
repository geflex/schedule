import re
from typing import Union, Pattern, Iterator

from bottex2.handler import Request
from bottex2.router import Condition


def if_text(s: str) -> Condition:
    s = s.lower()
    def cond(request: Request) -> bool:
        return request.text.lower() == s
    return cond


def if_regexp(exp: Union[str, Pattern]) -> Condition:
    exp = re.compile(exp)
    def cond(request: Request) -> bool:
        m = exp.match(request.text)
        return bool(m)
    return cond


def if_text_in(*wds: str) -> Condition:
    wds = [w.lower() for w in wds]
    def cond(request: Request) -> bool:
        return request.text.lower() in wds
    return cond


def if_in(conditions: Iterator[Condition]) -> Condition:
    def cond(request: Request):
        return any(c(request) for c in conditions)
    return cond