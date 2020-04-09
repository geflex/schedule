from abc import ABC, abstractmethod
from typing import Callable

from bottex.drivers import Request, Handler, Message, Button
from bottex.utils import regexp as re


class AbstractLink(ABC):
    def __init__(self,
                 handler: Handler,
                 response: Message = None,
                 next_handler: Handler = None):
        self._handler = handler
        self.handler = self._create_handler()
        self.response = response
        self.next_handler = next_handler

    @abstractmethod
    def match(self, request: Request) -> bool:
        pass

    def _create_handler(self):
        def new_handler(request):
            response = self._handler(request)
            if self.response:
                response = self.response << response
            if self.next_handler:
                next_resp = self.next_handler(request)
                if next_resp:
                    response = response << next_resp
            return response
        return new_handler

    def __repr__(self):
        return f'{self.__class__.__name__}' \
               f'(handler={self.handler}, ' \
               f'response={self.response}, ' \
               f'next_handler={self.next_handler})'


class FuncLink(AbstractLink):
    def __init__(self,
                 func: Callable[[Request], bool],
                 handler: Handler,
                 response: Message = None,
                 next_handler: Handler = None):
        super().__init__(handler, response, next_handler)
        self.func = func
        self.match = func

    def match(self, request):
        return self.func(request)


class StrictLink(AbstractLink):
    def __init__(self,
                 string: str,
                 handler: Handler,
                 response: Message = None,
                 next_handler: Handler = None):
        self.string = string
        super().__init__(handler, response, next_handler)

    def match(self, request):
        return self.string == request.msg


class ReLink(AbstractLink):
    def __init__(self,
                 regexp: str,
                 handler: Handler,
                 response: Message = None,
                 next_handler: Handler = None):
        self.regexp = re.compile(regexp)
        super().__init__(handler, response, next_handler)

    def match(self, request):
        m = self.regexp.match(request.msg)
        if m:
            request.parsed = m
        return bool(m)


class ButtonLink(AbstractLink, Button):
    def __init__(self,
                 label: str,
                 handler: Handler,
                 response: Message = None,
                 next_handler: Handler = None,
                 *, color=None, next_line=True, translate=True):
        AbstractLink.__init__(self, handler, response, next_handler)
        Button.__init__(self, label, color, next_line=next_line, translate=translate)

    def match(self, request):
        return request.msg == self.label

    def __repr__(self):
        return f'{self.__class__.__name__}' \
               f'({self.label!r}, ' \
               f'handler={self.handler}, ' \
               f'response={self.response}, ' \
               f'next_handler={self.next_handler}, ' \
               f'color={self.color}, ' \
               f'line={self.next_line})'


class InputLink(AbstractLink):
    def __init__(self,
                 handler: Handler,
                 response: Message = None,
                 next_handler: Handler = None):
        super().__init__(handler, response, next_handler)

    def match(self, request):
        return True
