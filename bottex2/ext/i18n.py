import gettext
from enum import Enum
from typing import Optional

from bottex2.bottex import BottexChatMiddleware, BottexHandlerMiddleware
from bottex2.chat import Keyboard
from bottex2.handler import Request


class LazyTranslate(str):
    def __init__(self, s, domain=None):
        super().__init__(s)
        self.domain = domain

    def format(self, *args, **kwargs):
        self.fmt_args = args
        self.fmt_kwargs = kwargs
        return self

    @classmethod
    def check(cls, s):
        return hasattr(s, 'fmt_args') and hasattr(s, 'fmt_kwargs')

    # noinspection PyUnresolvedReferences
    @classmethod
    def enforce(cls, s: str, fmt_data: Optional[str] = None):
        if cls.check(s):
            return super().format(s, *s.fmt_args, **s.fmt_kwargs)
        elif cls.check(fmt_data):
            return s.format(*fmt_data.fmt_args, **fmt_data.fmt_kwargs)


def _(s, domain=None):
    return LazyTranslate(s, domain)


class I18nUserMixin:
    locale: Enum


def translate(text, lang):
    try:
        trans = gettext.translation('schedule', 'schedule/locales', [lang])
    except FileNotFoundError:
        return LazyTranslate.enforce(text)
    else:
        return LazyTranslate.enforce(trans.gettext(text), text)


class TranslateBottexChatMiddleware(BottexChatMiddleware):
    __universal__ = True
    lang: Enum

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
    lang: Enum

    async def __call__(self, request: Request):
        lang = request.user.locale
        request.chat.lang = lang
        # request.text = translate(request.text, lang.value)
        await super().__call__(request)
