from typing import Callable

from bottex.drivers import Request, Handler, Message, Button
from bottex.utils import regexp as re
from bottex.views.views import Link


class FuncLink(Link):
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


class StrictLink(Link):
    def __init__(self,
                 string: str,
                 handler: Handler,
                 response: Message = None,
                 next_handler: Handler = None):
        self.string = string
        super().__init__(handler, response, next_handler)

    def match(self, request):
        return self.string.lower() == request.msg.text.lower()


class ReLink(Link):
    def __init__(self,
                 regexp: str,
                 handler: Handler,
                 response: Message = None,
                 next_handler: Handler = None):
        self.regexp = re.compile(regexp)
        super().__init__(handler, response, next_handler)

    def match(self, request):
        m = self.regexp.match(request.msg.text.lower())
        if m:
            request.parsed = m
        return bool(m)


class ButtonLink(Link, Button):
    def __init__(self,
                 label: str,
                 handler: Handler,
                 response: Message = None,
                 next_handler: Handler = None,
                 *, color=None, next_line=True, translate=True):
        Link.__init__(self, handler, response, next_handler)
        Button.__init__(self, label, color, next_line=next_line, translate=translate)

    def match(self, request):
        return request.msg.text.lower() == self.label.lower()

    def __repr__(self):
        return f'{self.__class__.__name__}' \
               f'({self.label!r}, ' \
               f'handler={self.handler}, ' \
               f'response={self.response}, ' \
               f'next_handler={self.next_handler}, ' \
               f'color={self.color}, ' \
               f'line={self.next_line})'


class InputLink(Link):
    def __init__(self,
                 handler: Handler,
                 response: Message = None,
                 next_handler: Handler = None):
        super().__init__(handler, response, next_handler)

    def match(self, request):
        return True
