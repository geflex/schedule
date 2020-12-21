from abc import abstractmethod, ABC
from typing import List, Optional, Awaitable

from bottex2.conditions import if_text_eq
from bottex2.handler import Request, Handler, Response, TResponse
from bottex2.helpers.tools import state_name
from bottex2.keyboard import Keyboard, Button
from bottex2.router import Router, TCondition


class Command:
    def __init__(self, text: str, callback: Handler, condition: Optional[TCondition] = None):
        self.text = text
        self.callback = callback
        self.condition = condition or if_text_eq(text)


class View(ABC):
    state_name: str

    def __init__(self, request: Request):
        self.r = request

    @property
    @abstractmethod
    def commands(self) -> List[List[Command]]:
        pass

    @property
    def keyboard(self) -> Keyboard:
        keyboard = Keyboard()
        for line in self.commands:
            keyboard.append_line()
            for command in line:
                keyboard.append_button(Button(command.text))
        return keyboard

    @property
    def router(self) -> Router:
        routes = {c.condition: c.callback for line in self.commands for c in line}
        return Router(routes, default=self.default)

    @classmethod
    def handle(cls, request: Request) -> Awaitable[TResponse]:
        return cls(request).router(request)

    def __call__(self, request: Request) -> Awaitable[TResponse]:
        return self.handle(request)

    async def default(self, r: Request) -> TResponse:
        return Response('Command not found', self.keyboard)

    @classmethod
    async def switch(cls, r: Request) -> TResponse:
        await r.user.update(state=state_name(cls))
        return
