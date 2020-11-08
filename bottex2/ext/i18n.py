import gettext
from enum import Enum
from typing import Optional

from bottex2.bottex import BottexChatMiddleware, BottexHandlerMiddleware
from bottex2.chat import Keyboard
from bottex2.handler import Request


class LazyTranslate(str):
    def __init__(self, s):
        super().__init__()
        self.domain = None

    def format(self, *args, **kwargs) -> 'LazyTranslate':
        self.fmt_args = args
        self.fmt_kwargs = kwargs
        return self

    def __str__(self) -> str:
        return self.enforce()

    def string(self) -> str:
        return super().__str__()

    def was_formatted(self) -> bool:
        return hasattr(self, 'fmt_args') and hasattr(self, 'fmt_kwargs')

    def enforce(self, s: Optional[str] = None) -> str:
        s = self.string() if s is None else s
        if self.was_formatted():
            return s.format(*self.fmt_args, **self.fmt_kwargs)
        return s


def _(s, domain):
    s = LazyTranslate(s)
    s.domain = domain
    return s


class I18nUserMixin:
    locale: Enum


def translate(text: str, lang):
    if isinstance(text, LazyTranslate):
        domain = text.domain
        try:
            trans = gettext.translation(domain, 'schedule/locales', [lang])
        except FileNotFoundError:
            return str(text)
        else:
            translated = trans.gettext(text)
            return text.enforce(translated)
    return text


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
