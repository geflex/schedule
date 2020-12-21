import asyncio
from collections import Iterable

from aiogram.bot import Bot

from bottex2 import multiplatform
from bottex2.ext.users import UserMiddleware
from bottex2.handler import Handler
from bottex2.middlewares import THandlerMiddleware
from bottex2.platforms._webhook import AioHttpTransportMixin
from bottex2.platforms.tg import TgUserMiddleware
from bottex2.server import Request


class TgWebHookReceiver(AioHttpTransportMixin):
    def __init__(self, handler: Handler,
                 middlewares: Iterable[THandlerMiddleware] = (), *,
                 token: str, host: str, port: int, path: str, ssl):
        super().__init__(handler, middlewares)
        self._token = token

        self._host = host
        self._port = port
        self._path = path
        self._requests_queue = asyncio.Queue()  # type: asyncio.Queue[dict]

    def parse_request(self, request: dict) -> Request:
        chat = TgChat(Bot(self._token), request['chat']['id'])
        text = request['message']['text']
        return Request(text=text, chat=chat, raw=request)


multiplatform.manager.register_child(UserMiddleware, TgWebHookReceiver, TgUserMiddleware)
