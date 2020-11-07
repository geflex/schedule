from typing import Iterator, Union, Pattern

from .handler import Request
from .router import Condition, if_text, if_in, if_regexp, if_text_in


class BaseCondition(Condition):
    def __call__(self, request: Request) -> bool:
        pass

class TextCond(BaseCondition):
    def __init__(self, s: str):
        self.string = s
        __call__ = if_text(self.string)

class AnyCond(BaseCondition):
    def __init__(self, conditions: Iterator[Condition]):
        self.conds = conditions
        self.__call__ = if_in(conditions)

class Reqexp(BaseCondition):
    def __init__(self, exp: Union[str, Pattern]):
        self.exp = exp
        self.__call__ = if_regexp(exp)

class Words(BaseCondition):
    def __init__(self, *words: str):
        self.words = words
        self.__call__ = if_text_in(*words)
