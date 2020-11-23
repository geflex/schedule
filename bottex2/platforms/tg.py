import asyncio
from typing import Optional, AsyncIterator, Type, Iterable

import aiogram
import aiohttp

from bottex2 import bottex
from bottex2.chat import AbstractChat, Keyboard
from bottex2.ext.users import UserBottexMiddleware
from bottex2.handler import Request, HandlerMiddleware, Handler
from bottex2.logging import logger
from bottex2.server import Server


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


class TgServer(Server):
    def __init__(self, handler: Handler,
                 middlewares: Iterable[Type[HandlerMiddleware]] = (),
                 *, token: str):
        super().__init__(handler, middlewares)
        self.bot = aiogram.Bot(token)

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
                        chat = TgChat(self.bot, raw['chat']['id'])
                        yield Request(text=raw['text'],
                                      chat=chat,
                                      raw=raw)


class TgUserHandlerMiddleware(UserBottexMiddleware):
    async def get_user(self, request: Request):
        uid = request.raw['from']['id']
        return await self.get_or_create('tg', uid)


bottex.manager.register_child(UserBottexMiddleware, TgServer, TgUserHandlerMiddleware)
