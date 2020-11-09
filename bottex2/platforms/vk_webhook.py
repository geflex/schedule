import asyncio

from aiovk.sessions import TokenSession

from bottex2.ext import users
from bottex2.platforms._webhook import AioHttpReceiverMixin, InvalidRequest
from bottex2.platforms.vk import VkChat, VkUserHandlerMiddleware
from bottex2.receiver import Request


class VkCallbackReceiver(AioHttpReceiverMixin):
    def __init__(self, *, token: str, group_id: str, host: str, port: int, path: str, secret: str):
        super().__init__()
        self._token = token
        self._session = TokenSession(token)

        self._host = host
        self._port = port
        self._path = path
        self._requests_queue = asyncio.Queue()  # type: asyncio.Queue[dict]
        self._secret = secret

    def parse_request(self, request: dict) -> Request:
        try:
            if request['secret'] != self._secret:
                raise InvalidRequest(f'Invalid secret key: {request["secret"]}')
            message = request['object']['message']
            text = message['text']
            from_id = message['from_id']
        except KeyError as e:
            raise InvalidRequest(e) from e
        else:
            chat = VkChat(self._session, from_id)
            return Request(text=text, chat=chat, raw=request)


users.UserBottexHandlerMiddleware.submiddleware(VkCallbackReceiver, VkUserHandlerMiddleware)