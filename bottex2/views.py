from abc import abstractmethod, ABC
from typing import List

from bottex2.chat import Keyboard, Button
from bottex2.handler import Request
from bottex2.router import Router, text_cond


class Command:
    def __init__(self, text: str, callback):
        self.text = text
        self.callback = callback


class View(ABC):
    def __init__(self, request: Request):
        self.r = request
        self.commands = self.init_commands()
        self.keyboard = self.init_keyboard()
        self.router = self.init_router()

    @abstractmethod
    def init_commands(self) -> List[List[Command]]:
        pass

    def init_keyboard(self) -> Keyboard:
        keyboard = Keyboard()
        for line in self.commands:
            keyboard.add_line()
            for command in line:
                keyboard.add_button(Button(command.text))
        return keyboard

    def init_router(self) -> Router:
        router = Router(default=self.default)
        for line in self.commands:
            for command in line:
                router.add_route(text_cond(command.text), command.callback)
        return router

    async def handle(self):
        await self.router(self.r)

    @staticmethod
    async def default(r: Request):
        await r.chat.send_message('404')
