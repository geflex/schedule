import asyncio

from aiovk.sessions import TokenSession

from bottex2.platforms._webhook import WebHookReceiverMixin
from bottex2.platforms.vk import VkChat, VkUserHandlerMiddleware
from bottex2.receiver import Request
from bottex2.middlewares import users


class VkCallbackReceiver(WebHookReceiverMixin):
    def __init__(self, *, token: str, host: str, port: int, path: str, ssl):
        super().__init__()
        self._token = token
        self._session = TokenSession(token)

        self._host = host
        self._port = port
        self._path = path
        self._requests_queue = asyncio.Queue()  # type: asyncio.Queue[dict]

    def yielder(self, request: dict) -> Request:
        message = request['object']['message']
        text = message['text']
        chat = VkChat(self._session, message['peer_id'])
        return Request(text=text, chat=chat, raw=request)


users.UserBottexHandlerMiddleware.submiddleware(VkCallbackReceiver, VkUserHandlerMiddleware)
