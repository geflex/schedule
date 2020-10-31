import datetime

from bottex2 import regexp as re

group_fmt = re.compile(r'\d{8}')
time_fmt = re.compile(r'(?P<hour>[01]?\d|2[0-3])[:.\-]?(?P<minute>[0-5]\d)')


def str_time(t):
    if isinstance(t, datetime.time):
        return f'{t:%H:%M}'
    return ''
