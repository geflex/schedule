from datetime import time, date, timedelta


class Time:
    def __init__(self, t):
        self.time = t

    def str(self):
        return self.time.strftime('%H:%M')

    @staticmethod
    def parse(s):
        h, m = s.split(':', 1)
        return time(int(h), int(m))


class Date(date):
    def days_add(self, n):
        return self + timedelta(days=n)

    def days_sub(self, n):
        return self - timedelta(days=n)
