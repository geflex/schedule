import gettext
from enum import Enum
from typing import List, Optional, Dict

from sqlalchemy import Column, types as sqltypes

from bottex2.chat import Keyboard
from bottex2.bottex import BottexChatMiddleware, BottexHandlerMiddleware
from bottex2.handler import Request


class Lang(Enum):
    ru = 'ru'
    en = 'en'
    be = 'be'


class I18nUserMixin:
    locale = Column(sqltypes.Enum(Lang))


class TranslateBottexChatMiddleware(BottexChatMiddleware):
    __universal__ = True

    async def send_message(self, text: Optional[str] = None, kb: Optional[Keyboard] = None):
        locale = self.lang or Lang.ru
        try:
            trans = gettext.translation('schedule', 'schedule/locales', [locale.value])
        except FileNotFoundError:
            pass
        else:
            text = trans.gettext(text)
        await super().send_message(text, kb)


class TranslateBottexHandlerMiddleware(BottexHandlerMiddleware):
    __universal__ = True

    async def __call__(self, request: Request):
        request.chat.lang = request.user.locale
        await super().__call__(request)
