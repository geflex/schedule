from typing import Any, Awaitable

from bottex2.bottex import BottexMiddleware
from bottex2.logging import logger


class BottexLoggingMiddleware(BottexMiddleware):
    __unified__ = True

    async def __call__(self, request) -> Awaitable[Any]:
        logger.info(f'in : {request.text!r}')
        response = await self.handler(request)
        for message in response:
            logger.info(f'out: {message.text!r}')
        return response
