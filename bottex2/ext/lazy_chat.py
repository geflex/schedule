from dataclasses import dataclass
from typing import Optional

from bottex2.bottex import BottexMiddleware
from bottex2.chat import AbstractChat, Keyboard, ChatMiddleware
from bottex2.handler import Request


@dataclass
class Message:
    text: Optional[str]
    kb: Optional[Keyboard]


class LazyChatMiddleware(ChatMiddleware):
    def __init__(self, chat: AbstractChat):
        super().__init__(chat)
        self.responses = []

    async def send_message(self, text: Optional[str] = None, kb: Optional[Keyboard] = None):
        self.responses.append(Message(text=text, kb=kb))

    async def flush(self):
        for response in self.responses:
            await super().send_message(text=response.text, kb=response.kb)


class ResponseMiddleware(BottexMiddleware):
    __universal__ = True

    async def __call__(self, request: Request):
        chat = LazyChatMiddleware(request.chat)
        request.chat = chat
        await super().__call__(request)
        await chat.flush()
