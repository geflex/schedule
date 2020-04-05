from abc import ABC, abstractmethod

from bottex.messaging import Button, Message, Request
from bottex.typing import Receiver, Match, Optional as Opt
from bottex.utils import regexp as re


class AbstractLink(ABC):
    def __init__(self,
                 receiver: Receiver,
                 response: Message = None,
                 next_receiver: Receiver = None):
        self._receiver = receiver
        self.receiver = self._create_receiver()
        self.response = response
        self.next_receiver = next_receiver

    @abstractmethod
    def match(self, request: Request) -> bool:
        pass

    def _create_receiver(self):
        def new_receiver(request):
            response = self._receiver(request)
            if self.response:
                response = self.response << response
            if self.next_receiver:
                next_resp = self.next_receiver(request)
                if next_resp:
                    response = response << next_resp
            return response
        return new_receiver

    def __repr__(self):
        return f'{self.__class__.__name__}' \
               f'(receiver={self.receiver}, ' \
               f'response={self.response}, ' \
               f'next_receiver={self.next_receiver})'


class FuncLink(AbstractLink):
    def __init__(self,
                 func: Match,
                 receiver: Receiver,
                 response: Message = None,
                 next_receiver: Receiver = None):
        super().__init__(receiver, response, next_receiver)
        self.func = func
        self.match = func

    def match(self, request):
        return self.func(request)


class StrictLink(AbstractLink):
    def __init__(self,
                 string: str,
                 receiver: Receiver,
                 response: Message = None,
                 next_receiver: Receiver = None):
        self.string = string
        super().__init__(receiver, response, next_receiver)

    def match(self, request):
        return self.string == request.msg


class ReLink(AbstractLink):
    def __init__(self,
                 regexp: str,
                 receiver: Receiver,
                 response: Message = None,
                 next_receiver: Receiver = None):
        self.regexp = re.compile(regexp)
        super().__init__(receiver, response, next_receiver)

    def match(self, request):
        m = self.regexp.match(request.msg)
        if m:
            request.parsed = m
        return bool(m)


class ButtonLink(AbstractLink, Button):
    def __init__(self,
                 label: str,
                 receiver: Receiver,
                 response: Message = None,
                 next_receiver: Receiver = None,
                 *, color=None, next_line=True, translated=True):
        AbstractLink.__init__(self, receiver, response, next_receiver)
        Button.__init__(self, label, color, next_line=next_line, translated=translated)

    def match(self, request):
        return request.msg == self.label

    def __repr__(self):
        return f'{self.__class__.__name__}' \
               f'({self.label!r}, ' \
               f'receiver={self.receiver}, ' \
               f'response={self.response}, ' \
               f'next_receiver={self.next_receiver}, ' \
               f'color={self.color}, ' \
               f'line={self.next_line})'


class InputLink(AbstractLink):
    def __init__(self,
                 receiver: Receiver,
                 response: Message = None,
                 next_receiver: Receiver = None):
        super().__init__(receiver, response, next_receiver)

    def match(self, request):
        return True
