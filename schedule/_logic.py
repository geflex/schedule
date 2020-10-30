from datetime import timedelta, date
from typing import List, Tuple, Collection

from . import models


_splitter = '\n' + '='*28 + '\n'

def _str_lesson(lesson: models.Lesson):
    return f'{lesson.time} {lesson.auditories} к{lesson.building}\n{lesson.name}'

def str_week(lessons: Collection[models.Lesson]) -> List[str]:
    days = {}
    for lesson in lessons:
        day = days.setdefault(lesson.weekday.name, [])
        day.append(lesson)
    response = []
    for day_name, day_lessons in days.items():
        day_str = f'> > > {day_name}{_splitter}{str_day(day_lessons)}'
        response.append(day_str)
    return response


def str_day(lessons: Collection[models.Lesson]):
    str_lessons = []
    for lesson in lessons:
        s = _str_lesson(lesson)
        str_lessons.append(s)
    if not str_lessons:
        return 'Занятий нет'
    return _splitter.join(str_lessons)


class Date(date):
    def days_incr(self, n):
        return self + timedelta(days=n)

    def days_decr(self, n):
        return self - timedelta(days=n)


def course_start(dt: date) -> Date:
    year = dt.year if dt.month >= 9 else dt.year - 1
    first_sept = Date(year, 9, 1)
    if first_sept.weekday() == 6:
        return Date(year, 9, 2)
    return Date(year, 9, 1)


def get_week_num(dt: date) -> int:
    delta = dt - course_start(dt)
    total_weeks = delta // timedelta(weeks=1)
    return total_weeks % 2 + 1


def get_week_range(dt: date) -> Tuple[date, date]:
    day_num = dt.weekday()
    monday_date = dt - timedelta(days=day_num)
    next_monday_date = monday_date + timedelta(days=6)
    return monday_date, next_monday_date


def get_day_lessons(dt, **kwargs):
    result = models.Lesson.objects(weekday=dt.weekday(),
                                   weeknum__in=[None, get_week_num(Date.today())],
                                   **kwargs)
    return result  # .order_by('time')


def get_week_lessons(week_num, **kwargs):
    result = models.Lesson.objects(weeknum__in=[None, week_num], **kwargs)
    return result


def day_lessons_str(dt, user: models.User):
    if user.ptype == models.PType.student:
        group, subgroup = user.group, user.subgroup
        objects = get_day_lessons(dt, group=str(group),
                                  subgroup__in=[None, subgroup])
    else:
        lastname = user.name
        objects = get_day_lessons(dt, teacher=lastname)
    return str_day(objects)


def week_lessons_str(week_num: int, user: models.User):
    if user.ptype == models.PType.student:
        group, subgroup = user.group, user.subgroup
        objects = get_week_lessons(week_num,
                                   group=str(group),
                                   subgroup__in=[None, subgroup])
    else:
        teacher = user.name
        objects = get_week_lessons(week_num, teacher=teacher)
    return str_week(objects)
