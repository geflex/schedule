import re
import string
import sre_parse
import sre_constants
import random


class Gen:
    def genfirst(self, values=None):
        pass
    def genlast(self, values=None):
        pass
    def genrand(self, values=None):
        pass


class Char(str, Gen):
    def __new__(cls, n):
        return super().__new__(cls, chr(n))
    def genfirst(self, values=None):
        return self
    def genlast(self, values=None):
        return self
    def genrand(self, values=None):
        return self


class Range(Gen):
    def __init__(self, data):
        self.min = data[0]
        self.max = data[1]
    def genfirst(self, values=None):
        return chr(self.min)
    def genlast(self, values=None):
        return chr(self.max)
    def genrand(self, values=None):
        return chr(random.randint(self.min, self.max))
    def __repr__(self):
        return f'{self.__class__.__name__}({chr(self.min)}-{chr(self.max)})'
    def __iter__(self):
        yield from (chr(i) for i in range(self.min, self.max))


class IterGen(list, Gen):
    def genfirst(self, values=None):
        return self[0].genfirst(values)
    def genlast(self, values=None):
        return self[-1].genlast(values)
    def genrand(self, values=None):
        return random.choice(self).genrand(values)
    def __repr__(self):
        values = ", ".join(repr(v) for v in self)
        return f'{self.__class__.__name__}({values})'


class In(IterGen):
    def __init__(self, data):
        super().__init__(_regen(data))
    def genfirst(self, values=None):
        return self[0].genfirst(values)
    def genlast(self, values=None):
        return self[-1].genlast(values)
    def genrand(self, values=None):
        return random.choice(self).genrand(values)


class List(IterGen):
    def genfirst(self, values=None):
        return ''.join(v.genfirst(values) for v in self)
    def genlast(self, values=None):
        return ''.join(v.genlast(values) for v in self)
    def genrand(self, values=None):
        return ''.join(v.genrand(values) for v in self)


class Subpattern(List):
    def __init__(self, data):
        self.num = data[0]
        super().__init__(_regen(data[3]))

    def genfirst(self, values=None):
        if values and self.num in values:
            return values[self.num]
        return ''.join(v.genfirst(values) for v in self)

    def genlast(self, values=None):
        if values and self.num in values:
            return values[self.num]
        return ''.join(v.genlast(values) for v in self)

    def genrand(self, values=None):
        if values and self.num in values:
            return values[self.num]
        return ''.join(v.genrand(values) for v in self)


class Or(IterGen):
    def __init__(self, data):
        super().__init__(_regen(data[1]))


class MaxRepeat(IterGen):
    def __init__(self, data):
        self.min = data[0]
        self.max = data[1]
        super().__init__(_regen(data[2]))
    def num(self):
        return self.min or 1
        # return random.randint(self.min, self.max)
    def genrand(self, values=None):
        return ''.join(''.join(v.genrand(values) for v in self) for _ in range(self.num()))
    def genfirst(self, values=None):
        return self[0].genfirst(values) * self.num()
    def genlast(self, values=None):
        return self[-1].genlast(values) * self.num()


class Category(IterGen):
    categories = {
        'CATEGORY_DIGIT': (string.digits, '\\d'),
        'CATEGORY_SPACE': (string.whitespace, '\\s'),
        'CATEGORY_WORD': (string.ascii_letters, '\\w'),
    }
    def __init__(self, data):
        category = self.categories[data.name]
        self.symbol = category[1]
        super().__init__(category[0])
    def genfirst(self, values=None):
        return self[0]
    def genlast(self, values=None):
        return self[-1]
    def genrand(self, values=None):
        return random.choice(self)


classes = {
    sre_constants.LITERAL: Char,
    sre_constants.RANGE: Range,
    sre_constants.IN: In,
    sre_constants.SUBPATTERN: Subpattern,
    sre_constants.BRANCH: Or,
    sre_constants.MAX_REPEAT: MaxRepeat,
    sre_constants.CATEGORY: Category,
}


def _regen(data):
    if hasattr(data, 'data'):
        data = data.data
    if isinstance(data, (list, tuple)):
        clsname = data[0]
        if isinstance(clsname, sre_constants._NamedIntConstant):
            cls = classes[clsname]
            return cls(data[1])
        return List(_regen(v) for v in data)
    raise ValueError('invalid pattern')


class Pattern(Gen):
    def __init__(self, pattern, flags=0):
        self._pattern = re.compile(pattern, flags=0)
        if isinstance(pattern, re.Pattern):
            pattern = pattern.pattern
        parsed = sre_parse.parse(pattern, flags)
        self._gen = _regen(parsed)

    @property
    def pattern(self):
        return self._pattern.pattern

    def _merge_args(self, values, kwargs):
        args = {n+1: v for n, v in enumerate(values)}
        nums = self._pattern.groupindex
        kwargs = {nums[gr]: v for gr, v in kwargs.items()}
        args.update(kwargs)
        return args

    def genfirst(self, *values, **kwargs):
        values = self._merge_args(values, kwargs)
        return self._gen.genfirst(values)

    def genlast(self, *values, **kwargs):
        values = self._merge_args(values, kwargs)
        return self._gen.genlast(values)

    def genrand(self, *values, **kwargs):
        values = self._merge_args(values, kwargs)
        return self._gen.genrand(values)

    def match(self, s, **kwargs):
        return self._pattern.match(s, **kwargs)
    def fullmatch(self, s, **kwargs):
        return self._pattern.fullmatch(s, **kwargs)
    def search(self, s, **kwargs):
        return self._pattern.search(s, **kwargs)
    def sub(self, repl, s, count=0):
        return self._pattern.sub(repl, s, count)
    def subn(self, repl, s, count=0):
        return self._pattern.subn(repl, s, count)
    def split(self, s, maxsplit=0):
        return self._pattern.split(s, maxsplit)
    def findall(self, s, **kwargs):
        return self._pattern.findall(s, **kwargs)
    def finditer(self, s, **kwargs):
        return self._pattern.finditer(s, **kwargs)

    def __repr__(self):
        return repr(self._pattern)


# noinspection PyShadowingBuiltins
def compile(pattern, flags=0):
    if isinstance(pattern, Pattern):
        return pattern
    return Pattern(pattern, flags)
