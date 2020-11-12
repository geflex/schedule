from datetime import timedelta, date
from typing import Tuple


class Date(date):
    @classmethod
    def tomorrow(cls):
        return cls.today().days_incr(1)

    @classmethod
    def yesterday(cls):
        return cls.today().days_decr(1)

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
