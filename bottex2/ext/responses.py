from typing import Optional, Iterable

from bottex2.bottex import BottexMiddleware
from bottex2.chat import Keyboard
from bottex2.handler import Request, Message


def response_factory(text: Optional[str] = None, kb: Optional[Keyboard] = None):
    return Message(text, kb)


class ResponseBottexMiddleware(BottexMiddleware):
    __unified__ = True

    async def __call__(self, request: Request):
        request.resp = response_factory
        response = await super().__call__(request)
        if isinstance(response, Iterable):
            for resp in response:
                await request.chat.send_message(resp.text, resp.kb)
