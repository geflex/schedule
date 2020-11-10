import gettext as gettext_module
from enum import Enum
from functools import partial
from typing import Optional

from bottex2.bottex import BottexMiddleware
from bottex2.chat import Keyboard, AbstractChat, ChatMiddleware
from bottex2.handler import Request
from bottex2.logging import logger


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


REVERSIBLE_DOMAIN = 'reversible'
REVERSED_DOMAIN = 'reversed'
default_lang: Optional[str] = None


def set_default_lang(lang: str):
    global default_lang
    default_lang = lang


def gettext(s, domain):
    s = LazyTranslate(s)
    s.domain = domain
    return s


rgettext = partial(gettext, domain=REVERSIBLE_DOMAIN)


class I18nUserMixin:
    locale: Enum


def translate(text: str, lang: str):
    if isinstance(text, LazyTranslate) and lang != default_lang:
        domain = text.domain
        try:
            trans = gettext_module.translation(domain, 'schedule/locales', [lang])
        except FileNotFoundError as e:
            logger.warn(e)
            return str(text)
        else:
            translated = trans.gettext(text)
            return text.enforce(translated)
    return text


class TranslateBottexChatMiddleware(ChatMiddleware):
    def __init__(self, chat: AbstractChat, lang: Enum):
        super().__init__(chat)
        self.lang = lang

    def translate(self, text):
        # noinspection PyTypeChecker
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


class TranslateBottexMiddleware(BottexMiddleware):
    __universal__ = True
    lang: Enum

    async def __call__(self, request: Request):
        lang = request.user.locale
        request.chat = TranslateBottexChatMiddleware(request.chat, lang)
        text = gettext(request.text, REVERSED_DOMAIN)
        request.text = translate(text, lang.value)
        await super().__call__(request)
