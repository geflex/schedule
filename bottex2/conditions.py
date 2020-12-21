import re
from typing import Union, Pattern, Iterator

from bottex2.handler import Request
from bottex2.router import TCondition


def if_text_eq(s: str) -> TCondition:
    s = s.lower()
    def cond(r: Request) -> bool:
        return r.text.lower() == s
    return cond


def if_text_contains(s: str) -> TCondition:
    s = s.lower()
    def cond(r: Request) -> bool:
        return s in r.text.lower()
    return cond


def if_re_match(exp: Union[str, Pattern]) -> TCondition:
    exp = re.compile(exp)
    def cond(r: Request) -> bool:
        m = exp.match(r.text)
        return bool(m)
    return cond


def if_text_in(*wds: str) -> TCondition:
    wds = [w.lower() for w in wds]
    def cond(r: Request) -> bool:
        return r.text.lower() in wds
    return cond


def if_any(conditions: Iterator[TCondition]) -> TCondition:
    def cond(r: Request):
        return any(c(r) for c in conditions)
    return cond
