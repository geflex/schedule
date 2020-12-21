import asyncio
from collections import Iterable

import aiohttp.web
from aiovk.sessions import TokenSession

from bottex2 import multiplatform
from bottex2.ext.users import UserMiddleware
from bottex2.handler import Handler
from bottex2.middlewares import THandlerMiddleware
from bottex2.platforms._webhook import AioHttpTransportMixin, InvalidRequest
from bottex2.platforms.vk import VkUserMiddleware
from bottex2.server import Request


class VkCallbackReceiver(AioHttpTransportMixin):
    def __init__(self, handler: Handler,
                 middlewares: Iterable[THandlerMiddleware] = (), *,
                 token: str, group_id: str, host: str, port: int, path: str, secret: str, confirmation: str):
        super().__init__(handler, middlewares)
        self._token = token
        self._session = TokenSession(token)
        self._group_id = group_id

        self._host = host
        self._port = port
        self._path = path
        self._requests_queue = asyncio.Queue()  # type: asyncio.Queue[dict]
        self._secret = secret
        self._confirmation = confirmation

    def parse_request(self, request: dict) -> Request:
        try:
            if request['type'] == 'confirmation' and request['group_id'] == self._group_id:
                self.response(aiohttp.web.Response(body=self._confirmation))
                return
            if request['secret'] != self._secret:
                raise InvalidRequest(f'Invalid secret key: {request["secret"]}')
            message = request['object']['message']
            text = message['text']
            from_id = message['from_id']
        except KeyError as e:
            raise InvalidRequest(e) from e
        else:
            self.response(aiohttp.web.Response(headers=self.headers))
            chat = VkChat(self._session, from_id)
            return Request(text=text, chat=chat, raw=request)


multiplatform.manager.register_child(UserMiddleware, VkCallbackReceiver, VkUserMiddleware)
