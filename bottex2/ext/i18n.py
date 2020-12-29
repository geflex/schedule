from __future__ import annotations

import gettext as gettext_module
from abc import ABC, abstractmethod
from functools import partial
from typing import Optional, Type, Union

from sqlalchemy import Column
from sqlalchemy import types as satypes

from bottex2.handler import Request, TResponse
from bottex2.helpers import tables
from bottex2.keyboard import Keyboard
from bottex2.logging import logger
from bottex2.multiplatform import MultiplatformMiddleware


class Translatable(str):
    def __init__(self, s):
        super().__init__()
        self.domain = None
        self.formatted = False
        self.capitalized = False

    @classmethod
    def init(cls, s: str, domain: str):
        obj = cls(s)
        obj.domain = domain
        return obj

    def format(self, *args, **kwargs) -> Translatable:
        self.fmt_args = args
        self.fmt_kwargs = kwargs
        self.formatted = True
        return self

    def capitalize(self) -> Translatable:
        self.capitalized = True
        return self

    def __str__(self) -> str:
        return self.enforce()

    def string(self) -> str:
        return super().__str__()

    def enforce(self, translated: Optional[str] = None) -> str:
        """
        Accepts all transformations to self or to translated
        """
        s = self.string() if translated is None else translated
        if self.formatted:
            s = s.format(*self.fmt_args, **self.fmt_kwargs)
        if self.capitalized:
            s = s.capitalize()
        return s


class BaseLang(tables.Table):
    abbr = tables.Column(primary=True)
    name = tables.Column()


class I18nUserMixin:
    locale: BaseLang


def translate(text: Union[str, Translatable], lang: str,
              lcdir: str, default_lang: Optional[str] = None):
    if isinstance(text, Translatable) and lang != default_lang:
        domain = text.domain
        try:
            trans = gettext_module.translation(domain, lcdir, [lang])
        except FileNotFoundError as e:
            logger.warn(e)
            return str(text)
        else:
            translated = trans.gettext(text)
            return text.enforce(translated)
    return text


class MultiplatformI18nMiddleware(MultiplatformMiddleware, ABC):
    __unified__ = True

    reversed_domain: str

    @classmethod
    @abstractmethod
    def translate(cls, text: str, locale: str) -> str:
        pass

    @classmethod
    def tranlate_keyboard(cls, kb: Optional[Keyboard], locale: str) -> Optional[Keyboard]:
        if kb is None:
            return kb
        for line in kb:
            for button in line:
                button.label = cls.translate(button.label, locale)  # !!! Changing an existing kb
        return kb

    @classmethod
    def translate_response(cls, response: TResponse, locale: str) -> TResponse:
        if response is None:
            return
        for message in response:
            # !!! Changing an existing response
            message.text = cls.translate(message.text, locale)
            message.kb = cls.tranlate_keyboard(message.kb, locale)
        return response

    async def __call__(self, request: Request):
        user = request.user  # type: I18nUserMixin
        text = Translatable.init(request.text, self.reversed_domain)
        request.text = self.translate(text, user.locale.abbr)  # !!! Changing an existing request

        response = await super().__call__(request)
        return self.translate_response(response, user.locale.abbr)


class I18n:
    def __init__(self,
                 lang_table: Type[BaseLang],
                 default_lang: BaseLang,
                 lcdir: str,
                 domain_name: str,
                 reversed_domain='reversed',
                 reversible_domain='reversible'):
        self.Lang = lang_table
        self.default_lang = default_lang
        self.lcdir = lcdir
        self.reversed_domain = reversed_domain
        self.reversible_domain = reversible_domain

        self.translate = partial(translate, default_lang=default_lang)
        self.gettext = partial(Translatable.init, domain=domain_name)
        self.rgettext = partial(Translatable.init, domain=reversible_domain)

        self.Middleware = type('MultiplatformI18nMiddleware', (MultiplatformI18nMiddleware,), {
            'translate': partial(translate, default_lang=default_lang, lcdir=lcdir),
            'reversed_domain': reversed_domain,
        })

        self.UserMixin = type('I18nUserMixin', (I18nUserMixin, ), {
            'locale': Column(satypes.Enum(lang_table, name='lang'),
                             default=default_lang, nullable=False)
        })
