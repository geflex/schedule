from datetime import timedelta

from bottex.drivers import Text, Message
from bottex.utils.i18n import gettext as _

from date_utils import Date
from models import Lesson, PType


class Formatter:
    splitter = '\n' + '='*28 + '\n'

    def str_lesson(self, lesson: Lesson):
        return f'{lesson.time} {lesson.auditory} к{lesson.building}\n{lesson.name}'

    def format_day(self, db_objects):
        if not db_objects:
            return _('Занятий нет')
        lessons = []
        for lesson in db_objects:
            s = self.str_lesson(lesson)
            lessons.append(s)
        return self.splitter.join(lessons)

    def format_week(self, db_objects):
        days = {}
        for lesson in db_objects:
            day = days.setdefault(lesson.weekday.name, [])
            day.append(lesson)
        resp = Message()
        for day, lessons in days.items():
            day_str = f'> > > {day}{self.splitter}{self.format_day(lessons)}'
            resp.append(Text(day_str))
        return resp


def _today():
    return Date.today()


def _course_start(dt):
    year = dt.year if dt.month >= 9 else dt.year - 1
    first_sept = Date(year, 9, 1)
    if first_sept.weekday() == 6:
        return Date(year, 9, 2)
    return Date(year, 9, 1)


def _weeknum(dt) -> int:
    delta = dt - _course_start(dt)
    total_weeks = delta // timedelta(weeks=1)
    return total_weeks % 2 + 1


def _weekday(dt):
    return dt.weekday()


def _week_range(dt):
    day_num = dt.weekday()
    monday = dt - timedelta(days=day_num)
    return monday, monday + timedelta(days=6)


def _db_day(dt, **kwargs):
    result = Lesson.objects(weekday=_weekday(dt),
                            weeknum__in=[None, _weeknum(_today())],
                            **kwargs)
    return result  # .order_by('time')


def _day(dt, request):
    if request.user.ptype == PType.student:
        group, subgroup = request.user.group, request.user.subgroup
        objects = _db_day(dt, group=str(group),
                          subgroup__in=[None, subgroup])
    else:
        lastname = request.user.name
        objects = _db_day(dt, teacher=lastname)
    result = Formatter().format_day(objects)
    return Text(result)


def today_schedule(request):
    return _day(_today(), request)


def tomorrow_schedule(request):
    dt = _today().days_add(1)
    return _day(dt, request)


def _db_week(weeknum, **kwargs):
    result = Lesson.objects(weeknum__in=[None, weeknum], **kwargs)
    return result


def _week(weeknum, request):
    if request.user.ptype == PType.student:
        group, subgroup = request.user.group, request.user.subgroup
        objects = _db_week(weeknum,
                           group=str(group),
                           subgroup__in=[None, subgroup])
    else:
        teacher = request.user.name
        objects = _db_week(weeknum, teacher=teacher)
    result = Formatter().format_week(objects)
    return result


def curr_week(request):
    weeknum = _weeknum(_today())
    return _week(weeknum, request)


def next_week(request):
    weeknum = _weeknum(_today()) + 1
    return _week(weeknum, request)


def week_num(request):
    n = _weeknum(_today())
    return Text(_(f'{n} неделя'))
