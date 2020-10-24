import sys
from random import randint
import json
import aiohttp
from typing import Union, Optional, AsyncIterator
import asyncio

from aiovk import API
from aiovk.sessions import BaseSession, TokenSession
from aiovk.longpoll import BotsLongPoll

from bottex2.handler import HandlerMiddleware, Request
from bottex2.chat import Chat, Keyboard
from bottex2.receiver import Receiver
from bottex2.middlewares import users


class VkChat(Chat):
    def __init__(self, session: BaseSession, peer_id: Union[int, str]):
        super().__init__()
        self._api = API(session)
        self._peer_id = peer_id

    def _prepare_kb(self, kb: Optional[Keyboard]):
        if kb is None:
            return ''
        json_buttons = []
        json_kb = {'one_time': kb.one_time,
                   'buttons': json_buttons}
        for line in kb:
            json_line = []
            json_buttons.append(json_line)
            for button in line:
                json_line.append({
                    'action': {
                        'type': 'text',
                        'label': button.label
                    },
                    'color': 'secondary',
                })
        return json.dumps(json_kb)

    async def send_message(self, text: Optional[str] = None,
                           kb: Optional[Keyboard] = None):
        try:
            await self._api.messages.send(random_id=randint(0, sys.maxsize),
                                          user_id=self._peer_id,
                                          message=text,
                                          keyboard=self._prepare_kb(kb))
        except (asyncio.TimeoutError, aiohttp.ClientOSError):
            pass


class VkReceiver(Receiver):
    def __init__(self, config_filename):
        super().__init__()
        with open(config_filename) as f:
            config = json.load(f)
        self.session = TokenSession(access_token=config['token'])
        self._longpoll = BotsLongPoll(self.session, mode=0, group_id=config['group_id'])

    async def listen(self) -> AsyncIterator[Request]:
        while True:
            try:
                response = await self._longpoll.wait(need_pts=True)
            except asyncio.TimeoutError:
                continue

            for event in response['updates']:
                if event['type'] == 'message_new':
                    message = event['object']['message']
                    chat = VkChat(self.session, message['peer_id'])
                    yield Request(text=message['text'],
                                  chat=self.wrap_chat(chat),
                                  raw=event)


@users.UserBottexHandlerMiddleware.submiddleware(VkReceiver)
class VkUserHandlerMiddleware(HandlerMiddleware):
    async def __call__(self, request: Request):
        uid = request.raw['object']['message']['from_id']
        request.user = await users.user_model.get('vk', uid)
        await self.handler(request)
