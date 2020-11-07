import gettext
from enum import Enum
from typing import Optional

from sqlalchemy import Column, types as sqltypes

from bottex2.bottex import BottexChatMiddleware, BottexHandlerMiddleware
from bottex2.chat import Keyboard
from bottex2.handler import Request


def _(s):
    return s


class Lang(Enum):
    ru = 'ru'
    en = 'en'
    be = 'be'


class I18nUserMixin:
    locale = Column(sqltypes.Enum(Lang))


def translate(text, lang):
    try:
        trans = gettext.translation('schedule', 'schedule/locales', [lang])
    except FileNotFoundError:
        return text
    else:
        return trans.gettext(text)


class TranslateBottexChatMiddleware(BottexChatMiddleware):
    __universal__ = True
    lang: Lang

    def translate(self, text):
        return translate(text, self.lang.value)

    def tranlate_keyboard(self, kb: Keyboard):
        for line in kb.buttons:
            for button in line:
                button.label = self.translate(button.label)
        return kb

    async def send_message(self, text: Optional[str] = None, kb: Optional[Keyboard] = None):
        text = self.translate(text)
        if kb:
            kb = self.tranlate_keyboard(kb)
        await super().send_message(text, kb)


class TranslateBottexHandlerMiddleware(BottexHandlerMiddleware):
    __universal__ = True

    async def __call__(self, request: Request):
        lang = request.user.locale or Lang.ru
        request.chat.lang = lang
        # request.text = translate(request.text, lang.value)
        await super().__call__(request)
