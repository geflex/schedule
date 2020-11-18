import gettext as gettext_module
from enum import Enum
from functools import partial
from typing import Optional, Iterable, Type

from sqlalchemy import Column
from sqlalchemy import types as sqltypes

from bottex2.bottex import BottexMiddleware
from bottex2.chat import Keyboard
from bottex2.handler import Request
from bottex2.logging import logger
from bottex2.messages import Message


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


def gettext(s, domain):
    s = LazyTranslate(s)
    s.domain = domain
    return s


class I18nUserMixin:
    locale: Enum


def translate(text: str, lang: str, default_lang: Optional[str] = None):
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


class I18nBottexMiddleware(BottexMiddleware):
    __unified__ = True

    default_lang: Enum
    reversed_domain: str

    @classmethod
    def translate(cls, text: str, locale: str):
        return translate(text, locale, default_lang=cls.default_lang.value)

    @classmethod
    def tranlate_keyboard(cls, kb: Keyboard, locale: str):
        for line in kb.buttons:
            for button in line:
                button.label = cls.translate(button.label, locale)
        return kb

    @classmethod
    def translate_response(cls, response: Iterable[Message], locale: str):
        # !!! It's a bad idea to change an existing response
        if response is None:
            return
        for message in response:
            message.text = cls.translate(message.text, locale)
            message.kb = cls.tranlate_keyboard(message.kb, locale)
        return response

    async def __call__(self, request: Request):
        user = request.user
        text = gettext(request.text, self.reversed_domain)
        request.text = self.translate(text, user.locale.value)

        response = await super().__call__(request)
        return self.translate_response(response, user.locale.value)


class I18nEnv:
    def __init__(self,
                 enum: Type[Enum],
                 default_lang: Enum,
                 domain: str,
                 reversed_domain='reversed',
                 reversible_domain='reversible'):
        self.enum = enum
        self.default_lang = default_lang
        self.reversed_domain = reversed_domain
        self.reversible_domain_name = reversible_domain

        self.translate = partial(translate, default_lang=default_lang)
        self.gettext = partial(gettext, domain=domain)
        self.rgettext = partial(gettext, domain=reversible_domain)

        self.Middleware = type('I18nBottexMiddleware', (I18nBottexMiddleware, ), {
            'default_lang': default_lang,
            'reversed_domain': reversed_domain,
        })

        self.UserMixin = type('I18nUserMixin', (I18nUserMixin, ), {
            'locale': Column(sqltypes.Enum(enum), default=default_lang, nullable=False)
        })
