from logging import Logger
from typing import Any

from bottex2.logging import logger as bottex_logger
from bottex2.multiplatform import MultiplatformMiddleware


class MultiplatformLoggingMiddleware(MultiplatformMiddleware):
    __unified__ = True
    logger: Logger

    async def __call__(self, request) -> Any:
        self.logger.info(f'in : {request.text!r}')
        response = await super().__call__(request)
        for message in response:
            self.logger.info(f'out: {message.text!r}')
        return response


class Logging:
    def __init__(self, logger=bottex_logger):
        self.logger = logger
        self.Middleware = type('LoggingMiddleware', (MultiplatformLoggingMiddleware,), {
            'logger': logger
        })
