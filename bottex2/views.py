from abc import abstractmethod, ABC
from functools import cached_property
from typing import List, Any, Awaitable

from bottex2.chat import Keyboard, Button
from bottex2.handler import Request, Handler
from bottex2.router import Router, if_text


class Command:
    def __init__(self, text: str, callback: Handler):
        self.text = text
        self.condition = if_text(text)
        self.callback = callback


class View(ABC):
    name: str

    def __init__(self, request: Request):
        self.r = request

    @cached_property
    @abstractmethod
    def commands(self) -> List[List[Command]]:
        pass

    @cached_property
    def keyboard(self) -> Keyboard:
        keyboard = Keyboard()
        for line in self.commands:
            keyboard.add_line()
            for command in line:
                keyboard.add_button(Button(command.text))
        return keyboard

    @cached_property
    def router(self) -> Router:
        router = Router(default=self.default)
        for line in self.commands:
            for command in line:
                router.add_route(command.condition, command.callback)
        return router

    @classmethod
    async def handle(cls, request: Request) -> Awaitable[Any]:
        return await cls(request).router(request)

    async def default(self, r: Request) -> Awaitable[Any]:
        return r.resp('404: command not found', self.keyboard)

    @classmethod
    async def switch(cls, r: Request) -> Awaitable[Any]:
        await r.user.update(state=cls.name)
        return None
