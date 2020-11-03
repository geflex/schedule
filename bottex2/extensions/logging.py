from typing import Optional

from bottex2.logging import logger
from bottex2.bottex import BottexHandlerMiddleware, BottexChatMiddleware
from bottex2.chat import Keyboard


class BottexLoggingHandlerMiddleware(BottexHandlerMiddleware):
    __universal__ = True

    async def __call__(self, request):
        logger.info(f'in: {request.text!r}')
        await self.handler(request)


class BottexLoggingChatMiddleware(BottexChatMiddleware):
    __universal__ = True

    async def send_message(self, text: Optional[str] = None, kb: Optional[Keyboard] = None):
        logger.info(f'out: {text!r}')
        await self.chat.send_message(text, kb)
