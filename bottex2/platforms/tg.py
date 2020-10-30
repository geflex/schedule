import aiohttp
import asyncio
from typing import Optional, AsyncIterator

import aiogram

from bottex2.handler import HandlerMiddleware, Request
from bottex2.chat import AbstractChat, Keyboard
from bottex2.receiver import Receiver
from bottex2.middlewares import users


class TgChat(AbstractChat):
    def __init__(self, bot: aiogram.Bot, chat_id):
        self.chat_id = chat_id
        self.bot = bot

    def _prepare_kb(self, kb: Optional[Keyboard]):
        if kb is None:
            return
        if kb.empty():
            json_kb = {'remove_keyboard': True}
        else:
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
    def __init__(self, token: str):
        super().__init__()
        self.bot = aiogram.Bot(token)

    async def listen(self) -> AsyncIterator[Request]:
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
                    yield Request(text=raw['text'],
                                  chat=self.wrap_chat(chat),
                                  raw=raw)


@users.UserBottexHandlerMiddleware.submiddleware(TgReceiver)
class TgUserHandlerMiddleware(HandlerMiddleware):
    async def __call__(self, request: Request):
        uid = request.raw['from']['id']
        request.user = await users.user_cls.get(platform='tg', uid=uid)
        await self.handler(request)
