import logging
from typing import Optional

from bottex2.bottex import BottexHandlerMiddleware, BottexChatMiddleware
from bottex2.chat import Keyboard


class LoggingBottexHandlerMiddleware(BottexHandlerMiddleware):
    async def __call__(self, text, **params):
        logging.info(f'received {text!r}')
        await self.handler(text=text, **params)


class LoggingBottexChatMiddleware(BottexChatMiddleware):
    async def send_message(self, text: Optional[str] = None, kb: Optional[Keyboard] = None):
        logging.info(f'sending {text!r}')
        await self.chat.send_message(text, kb)
