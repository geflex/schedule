import asyncio
from typing import Optional, AsyncIterator

import aiogram
import aiohttp

from bottex2 import multiplatform
from bottex2.ext.users import UserMiddleware
from bottex2.handler import Request
from bottex2.keyboard import Keyboard
from bottex2.logging import logger
from bottex2.server import Transport


class TgTransport(Transport):
    def __init__(self, token: str):
        self.bot = aiogram.Bot(token)

    def _button_dict(self, label: str):
        return {
            'text': label,
        }

    def _prepare_keyboard(self, kb: Keyboard):
        if kb is None:
            return
        if kb.empty():
            return {'remove_keyboard': True}

        json_buttons = []
        for line in kb:
            json_line = [self._button_dict(btn.label) for btn in line]
            json_buttons.append(json_line)

        return {
            'one_time_keyboard': kb.one_time,
            'keyboard': json_buttons,
        }

    async def listen(self) -> AsyncIterator[Request]:
        offset = None
        while True:
            try:
                updates = await self.bot.get_updates(offset=offset)
            except (asyncio.TimeoutError,
                    aiogram.exceptions.TelegramAPIError) as e:
                logger.error(repr(e))
            else:
                if updates:
                    offset = updates[-1].update_id + 1
                    for update in updates:
                        raw = update['message']
                        yield Request(text=raw['text'], raw=raw)

    async def send(self, request: Request,
                   text: Optional[str] = None,
                   kb: Optional[Keyboard] = None):
        keyboard = self._prepare_keyboard(kb)
        chat_id = request.raw['chat']['id']
        try:
            await self.bot.send_message(chat_id, text, reply_markup=keyboard)
        except (asyncio.TimeoutError, aiohttp.ClientOSError):
            pass


class TgUserMiddleware(UserMiddleware):
    def get_user(self, request: Request):
        uid = request.raw['from']['id']
        return self.get_or_create('tg', uid)


multiplatform.manager.register_child(UserMiddleware, TgTransport, TgUserMiddleware)
