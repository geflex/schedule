from abc import abstractmethod, ABC
from typing import List
from functools import cached_property

from bottex2.chat import Keyboard, Button
from bottex2.handler import Request
from bottex2.router import Router, text_cond


class Command:
    def __init__(self, text: str, callback):
        self.text = text
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
                router.add_route(text_cond(command.text), command.callback)
        return router

    @classmethod
    async def handle(cls, request: Request):
        await cls(request).router(request)

    @staticmethod
    async def default(r: Request):
        await r.chat.send_message('404')
