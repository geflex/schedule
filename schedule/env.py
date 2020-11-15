from enum import Enum
from functools import partial

from bottex2.ext.i18n import I18nEnv, gettext


class Lang(Enum):
    ru = 'ru'
    en = 'en'
    be = 'be'


i18n = I18nEnv(Lang, default_lang=Lang.ru)
i18n.gettext = partial(gettext, domain='schedule')
