from abc import abstractmethod, ABC
from typing import List, Optional

from bottex2.chat import Keyboard, Button
from bottex2.conditions import if_text_eq
from bottex2.handler import Request, Handler, Message
from bottex2.helpers.tools import state_name
from bottex2.router import Router, Condition


class Command:
    def __init__(self, text: str, callback: Handler, condition: Optional[Condition] = None):
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
            keyboard.add_line()
            for command in line:
                keyboard.add_button(Button(command.text))
        return keyboard

    @property
    def router(self) -> Router:
        router = Router(default=self.default)
        for line in self.commands:
            for command in line:
                router.add_route(command.condition, command.callback)
        return router

    @classmethod
    async def handle(cls, request: Request):
        return await cls(request).router(request)

    async def default(self, r: Request):
        return Message('Command not found', self.keyboard)

    @classmethod
    async def switch(cls, r: Request):
        await r.user.update(state=state_name(cls))
        return None  # !!!
