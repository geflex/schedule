from typing import Awaitable, Any, Callable, Optional, Iterable

from bottex2.keyboard import Keyboard


class Request(dict):
    text: str
    raw: Any

    def __init__(self, *, text: str, raw: Any, **params):
        super().__init__(text=text, raw=raw, **params)

    def __getattr__(self, attr):
        return self[attr]

    def copy(self):
        return Request(**self)


class Response:
    def __init__(self, text: Optional[str] = None, kb: Optional[Keyboard] = None):
        self.text = text
        self.kb = kb

    def __iter__(self):
        yield self


TResponse = Optional[Iterable[Response]]


class ErrorResponse(Exception):
    def __init__(self, resp: TResponse = None):
        self.resp = resp

    def __str__(self):
        return f'{[m.text for m in self.resp]}'


Handler = Callable[[Request], Awaitable[TResponse]]
