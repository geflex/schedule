import json
import aiohttp
import asyncio
from typing import Optional, AsyncIterator

import aiogram

from bottex2.handler import Params, HandlerMiddleware
from bottex2.chat import Chat, Keyboard
from bottex2.receiver import Receiver
from bottex2 import users


class TgChat(Chat):
    def __init__(self, bot: aiogram.Bot, chat_id):
        self.chat_id = chat_id
        self.bot = bot

    def _prepare_kb(self, kb: Optional[Keyboard]):
        if kb is None:
            return
        json_buttons = []
        json_kb = {
            'one_time_keyboard': kb.one_time,
            'keyboard': json_buttons
        }
        for line in kb:
            json_line = []
            json_buttons.append(json_line)
            for button in line:
                json_line.append({
                    'text': button.label,
                })
        return json_kb

    async def send_message(self, text: Optional[str] = None,
                           kb: Optional[Keyboard] = None):
        try:
            # noinspection PyTypeChecker
            await self.bot.send_message(self.chat_id, text, reply_markup=self._prepare_kb(kb))
        except (asyncio.TimeoutError, aiohttp.ClientOSError):
            pass


class TgReceiver(Receiver):
    def __init__(self, config_filename):
        super().__init__()
        with open(config_filename) as f:
            config = json.load(f)
        self.bot = aiogram.Bot(config['token'])

    async def listen(self) -> AsyncIterator[Params]:
        offset = None
        while True:
            try:
                updates = await self.bot.get_updates(offset=offset)
            except asyncio.TimeoutError:  # aiohttp.ClientOSError):
                continue
            if updates:
                offset = updates[-1].update_id + 1
                for update in updates:
                    raw = update['message']
                    chat = TgChat(self.bot, raw['chat']['id'])
                    yield Params(text=raw['text'],
                                 chat=self.wrap_chat(chat),
                                 raw=raw)


@users.UserBottexHandlerMiddleware.submiddleware(TgReceiver)
class TgUserHandlerMiddleware(HandlerMiddleware):
    async def __call__(self, raw: dict, **params):
        uid = raw['from']['id']
        user = await users.user_model.get('tg', uid)
        await self.handler(user=user, raw=raw, **params)
