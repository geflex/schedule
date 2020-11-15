import asyncio
from collections import Iterable
from typing import Type

from aiogram.bot import Bot

from bottex2 import bottex
from bottex2.ext.users import UserBottexMiddleware
from bottex2.handler import HandlerMiddleware
from bottex2.platforms._webhook import AioHttpReceiverMixin
from bottex2.platforms.tg import TgChat, TgUserHandlerMiddleware
from bottex2.receiver import Request


class TgWebHookReceiver(AioHttpReceiverMixin):
    def __init__(self, middlewares: Iterable[Type[HandlerMiddleware]] = (), *,
                 token: str, host: str, port: int, path: str, ssl):
        super().__init__(middlewares)
        self._token = token

        self._host = host
        self._port = port
        self._path = path
        self._requests_queue = asyncio.Queue()  # type: asyncio.Queue[dict]

    def parse_request(self, request: dict) -> Request:
        chat = TgChat(Bot(self._token), request['chat']['id'])
        text = request['message']['text']
        return Request(text=text, chat=chat, raw=request)


bottex.middlewares.register_child(UserBottexMiddleware, TgWebHookReceiver, TgUserHandlerMiddleware)
