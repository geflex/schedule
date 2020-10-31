from typing import Iterator, Union, Pattern

from .handler import Request
from .router import Condition, text_cond, any_cond, regexp_cond, words_cond


class BaseCondition(Condition):
    def __call__(self, request: Request) -> bool:
        pass

class TextCond(BaseCondition):
    def __init__(self, s: str):
        self.string = s
        __call__ = text_cond(self.string)

class AnyCond(BaseCondition):
    def __init__(self, conditions: Iterator[Condition]):
        self.conds = conditions
        self.__call__ = any_cond(conditions)

class Reqexp(BaseCondition):
    def __init__(self, exp: Union[str, Pattern]):
        self.exp = exp
        self.__call__ = regexp_cond(exp)

class Words(BaseCondition):
    def __init__(self, *words: str):
        self.words = words
        self.__call__ = words_cond(*words)
