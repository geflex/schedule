from abc import abstractmethod, ABC
from typing import List, Optional, Awaitable

from bottex2.conditions import if_text_eq
from bottex2.handler import Request, Handler, Response, TResponse
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

    @abstractmethod
    def commands(self) -> List[List[Command]]:
        pass

    @property
    def keyboard(self) -> Keyboard:
        keyboard = Keyboard()
        for line in self.commands():
            keyboard.append_line()
            for command in line:
                keyboard.append_button(Button(command.text))
        return keyboard

    @property
    def router(self) -> Router:
        routes = {c.condition: c.callback for line in self.commands() for c in line}
        return Router(routes, default=self.default)

    @classmethod
    def handle(cls, request: Request) -> Awaitable[TResponse]:
        return cls(request)(request)

    def wrap_response(self, response: TResponse):
        if response is not None:
            for resp in response:
                if resp.kb is None:
                    resp.kb = self.keyboard   # !!! changing existing response
        return response

    async def __call__(self, request: Request) -> TResponse:
        response = await self.router(request)
        return self.wrap_response(response)

    async def default(self, r: Request) -> TResponse:
        return Response('Command not found')

    async def switch(self) -> TResponse:
        await self.r.user.set_state(self.__class__)
        return None

    @classmethod
    async def switcher(cls, r: Request, response: TResponse = None) -> TResponse:
        obj = cls(r)
        default_response = await obj.switch()
        if response is None:
            response = default_response
        return obj.wrap_response(response)
