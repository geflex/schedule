import asyncio
import json
import sys
from random import randint
from typing import Optional, AsyncIterator

import aiohttp
from aiovk import API
from aiovk.exceptions import VkAPIError
from aiovk.longpoll import BotsLongPoll
from aiovk.sessions import TokenSession

from bottex2 import multiplatform
from bottex2.ext.users import UserMiddleware
from bottex2.handler import Request
from bottex2.keyboard import Keyboard
from bottex2.logging import logger
from bottex2.server import Transport


class VkTransport(Transport):
    def __init__(self, token: str, group_id: str):
        self._session = TokenSession(access_token=token)
        self._api = API(self._session)
        self._longpoll = BotsLongPoll(self._session, mode=0, group_id=group_id)

    def _button_dict(self, label):
        return {
            'action': {
                'type': 'text',
                'label': label
            },
            'color': 'secondary',
        }

    def _prepare_keyboard(self, kb: Optional[Keyboard]):
        if kb is None:
            return ''
        json_buttons = []
        if not kb.empty():
            for line in kb:
                if len(line) > 5:
                    logger.warning('vk keyboard line lenght > 5')
                    line = line[:5]
                dict_line = [self._button_dict(btn.label) for btn in line]
                json_buttons.append(dict_line)
        json_kb = {'one_time': kb.one_time,
                   'buttons': json_buttons}
        return json.dumps(json_kb)

    async def listen(self) -> AsyncIterator[Request]:
        while True:
            try:
                response = await self._longpoll.wait(need_pts=True)
            except (asyncio.TimeoutError, VkAPIError, aiohttp.ClientError) as e:
                logger.error(repr(e))
            else:
                for event in response['updates']:
                    if event['type'] == 'message_new':
                        message = event['object']['message']
                        yield Request(text=message['text'], raw=event)

    async def send(self, request: Request,
                   text: Optional[str] = None,
                   kb: Optional[Keyboard] = None):
        rand_id = randint(0, sys.maxsize)
        uid = request.raw['object']['message']['peer_id']
        keyboard = self._prepare_keyboard(kb)
        try:
            await self._api.messages.send(random_id=rand_id,
                                          user_id=uid,
                                          message=text,
                                          keyboard=keyboard)
        except (asyncio.TimeoutError, aiohttp.ClientOSError, VkAPIError) as e:
            logger.error(repr(e))


class VkUserMiddleware(UserMiddleware):
    def get_user(self, request: Request):
        uid = request.raw['object']['message']['from_id']
        return self.get_or_create('vk', uid)


multiplatform.manager.register_child(UserMiddleware, VkTransport, VkUserMiddleware)
