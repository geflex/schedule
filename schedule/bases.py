import datetime

from bottex.views.links import ButtonLink
from bottex.apis import Text
from bottex.apis.keyboard import Color
from bottex.utils.i18n import gettext as _
from bottex.utils import regexp as re


group_fmt = re.compile(r'\d{8}')
time_fmt = re.compile(r'(?P<hour>[01]?\d|2[0-3])[:.\-]?(?P<minute>[0-5]\d)')


def str_time(t):
    if isinstance(t, datetime.time):
        return f'{t:%H:%M}'
    return ''


class BackButton(ButtonLink):
    def __init__(self, callback, *, next_line=True):
        super().__init__(_('Назад'), callback, Text(_('Переходим назад')), color=Color.WHITE, next_line=next_line)


class CancelButton(ButtonLink):
    def __init__(self, callback, *, next_line=True):
        super().__init__(_('Отмена'), callback, Text(_('Отменяем')), color=Color.RED, next_line=next_line)


class NotChangeButton(ButtonLink):
    def __init__(self, callback, *, next_line=True):
        super().__init__(_('Не менять'), callback, Text(_('Не меняем')), color=Color.WHITE, next_line=next_line)


class PassButton(ButtonLink):
    def __init__(self, callback, *, next_line=True):
        super().__init__(_('Пропустить'), callback, Text(_('Пропускаем')), color=Color.WHITE, next_line=next_line)
