import datetime

from bottex2 import regexp as re
from bottex2.chat import Keyboard

group_fmt = re.compile(r'\d{8}')
time_fmt = re.compile(r'(?P<hour>[01]?\d|2[0-3])[:.\-]?(?P<minute>[0-5]\d)')


def str_time(t):
    if isinstance(t, datetime.time):
        return f'{t:%H:%M}'
    return ''


# class BackButton(ButtonLink):
#     def __init__(self, callback, *, next_line=True):
#         super().__init__('Назад', callback, 'Переходим назад', color=Color.WHITE, next_line=next_line)
#
#
# class CancelButton(ButtonLink):
#     def __init__(self, callback, *, next_line=True):
#         super().__init__('Отмена', callback, 'Отменяем', color=Color.RED, next_line=next_line)
#
#
# class NotChangeButton(ButtonLink):
#     def __init__(self, callback, *, next_line=True):
#         super().__init__('Не менять', callback, 'Не меняем', color=Color.WHITE, next_line=next_line)
#
#
# class PassButton(ButtonLink):
#     def __init__(self, callback, *, next_line=True):
#         super().__init__('Пропустить', callback, 'Пропускаем', color=Color.WHITE, next_line=next_line)
empty_kb = Keyboard([])