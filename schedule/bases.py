import random
import sys
import datetime

from bottex.views.links import ButtonLink
from bottex.messaging import Text
from bottex.messaging.keyboard import Color
from bottex.core.i18n import gettext as _
from bottex.utils import regexp as re


group_fmt = re.compile(r'\d{8}')
time_fmt = re.compile(r'(?P<hour>[01]?\d|2[0-3])[:.\-]?(?P<minute>[0-5]\d)')


def str_time(t):
    if isinstance(t, datetime.time):
        return f'{t:%H:%M}'
    return ''


class BackButton(ButtonLink):
    def __init__(self, receiver, *, next_line=True):
        super().__init__(_('Назад'), receiver, Text(_('Переходим назад')), color=Color.WHITE, next_line=next_line)


class CancelButton(ButtonLink):
    def __init__(self, receiver, *, next_line=True):
        super().__init__(_('Отмена'), receiver, Text(_('Отменяем')), color=Color.RED, next_line=next_line)


class NotChangeButton(ButtonLink):
    def __init__(self, receiver, *, next_line=True):
        super().__init__(_('Не менять'), receiver, Text(_('Не меняем')), color=Color.WHITE, next_line=next_line)


class PassButton(ButtonLink):
    def __init__(self, receiver, *, next_line=True):
        super().__init__(_('Пропустить'), receiver, Text(_('Пропускаем')), color=Color.WHITE, next_line=next_line)


def rand():
    return random.randint(0, sys.maxsize)
