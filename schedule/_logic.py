from datetime import timedelta, date
from typing import List, Tuple

from date_utils import Date
from models import User, Lesson, PType


class Formatter:
    splitter = '\n' + '='*28 + '\n'

    def str_lesson(self, lesson: Lesson):
        return f'{lesson.time} {lesson.auditories} к{lesson.building}\n{lesson.name}'

    def format_day(self, db_objects) -> str:
        lessons = []
        for lesson in db_objects:
            s = self.str_lesson(lesson)
            lessons.append(s)
        if not lessons:
            return 'Занятий нет'
        return self.splitter.join(lessons)

    def format_week(self, db_objects) -> List[str]:
        days = {}
        for lesson in db_objects:
            day = days.setdefault(lesson.weekday.name, [])
            day.append(lesson)
        response = []
        for day, lessons in days.items():
            day_str = f'> > > {day}{self.splitter}{self.format_day(lessons)}'
            response.append(day_str)
        return response


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
    result = Lesson.objects(weekday=dt.weekday(),
                            weeknum__in=[None, get_week_num(Date.today())],
                            **kwargs)
    return result  # .order_by('time')


def get_week_lessons(week_num, **kwargs):
    result = Lesson.objects(weeknum__in=[None, week_num], **kwargs)
    return result


def day_lessons_str(dt, user: User):
    if user.ptype == PType.student:
        group, subgroup = user.group, user.subgroup
        objects = get_day_lessons(dt, group=str(group),
                                  subgroup__in=[None, subgroup])
    else:
        lastname = user.name
        objects = get_day_lessons(dt, teacher=lastname)
    return Formatter().format_day(objects)


def week_lessons_str(week_num: int, user: User):
    if user.ptype == PType.student:
        group, subgroup = user.group, user.subgroup
        objects = get_week_lessons(week_num,
                                   group=str(group),
                                   subgroup__in=[None, subgroup])
    else:
        teacher = user.name
        objects = get_week_lessons(week_num, teacher=teacher)
    return Formatter().format_week(objects)
