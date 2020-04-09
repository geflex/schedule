from collections import defaultdict
import gettext as gettext_module


default_domain = 'bottex'
localedir = ''


class NullTranslation(gettext_module.NullTranslations):
    pass


null_translation = NullTranslation()


class BottexTranslation(gettext_module.GNUTranslations):
    def __init__(self, locale, domain=None, lcdir=None):
        super().__init__()
        self.locale = locale

    def __repr__(self):
        return f'<BottexTranslation locale={self.locale!r}>'


class LcManager:
    def __init__(self):
        self.locales = defaultdict()
        self.localedir = None

    def get_locale(self, locale):
        if locale not in self.locales:
            return NullTranslation()
        return self.locales[locale].gettext

    def add_locales(self, *locales):
        for locale in locales:
            self.locales[locale] = NullTranslation()  # gettext_module.translation('bottex', self.localedir, [locale])

    def set_default(self, locale):
        self.locales.setdefault(locale)


lc_manager = LcManager()


def get_locale(locale):
    return lc_manager.get_locale(locale)


def add_locales(*locales):
    lc_manager.add_locales(*locales)


def gettext(message):
    return message
