import xlrd
import re
import os
from itertools import zip_longest

from models import Lesson as DbLesson, WEEKDAYS

groups = {}
lessons = []
daynames = set()
words = set()
teachers = set()
buildings = set()
auditories = set()

exceptions = {
    'ф и з и ч е с к а я к у л ь т у р а': 'Физическая культура'
}


timepat = re.compile(r'[0-2]?\d\.[0-5]\d')
fulltimepat = re.compile(fr'(?P<start>{timepat.pattern})\s?-\s?(?P<end>{timepat.pattern})')


def sub_match(m):
    string = m.string
    return string[:m.start()] + string[m.end():]


_many_spaces = re.compile(r'\s+')
def normalize_spaces(s):
    return _many_spaces.sub(' ', s).strip()


class Borders:
    def __init__(self, top=False, left=False, bottom=False, right=False):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    def confined(self):
        return all([self.top, self.left, self.bottom, self.right])

    def __repr__(self):
        return f'Borders({self.top}, {self.left}, {self.bottom}, {self.right})'

    def prepr(self):
        ch = ' '
        l = '|' if self.left else ch
        t = '`' if self.top else ch
        b = '.' if self.bottom else ch
        r = '|' if self.right else ch
        return '('+l+t+b+r+')'


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __bool__(self):
        return bool(self.x and self.y)

    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self):
        return f'XY({self.x}, {self.y})'


class TextArea:
    def _gen_text(self):
        text = []
        for row in self._cells:
            for cell in row:
                v = cell.value
                if isinstance(v, float):
                    v = int(v)
                if v:
                    v = str(v).strip()
                    v = normalize_spaces(v)
                    text.append(v)
        return ' '.join(text)

    def __init__(self, start, end, cells=None):
        self.start = start
        self.end = end
        self._cells = list(cells) if cells is not None else []
        self.text = self._gen_text()
        self.parse()

    def parse(self):
        pass

    def set_cells(self, sheet):
        self._cells = list(sheet.slice(self.start, self.end))
        self.text = self._gen_text()

    @classmethod
    def copy_area(cls, area: 'TextArea'):
        return cls(area.start, area.end, area._cells)

    def xrange(self):
        return range(self.start.x, self.end.x)

    def yrange(self):
        return range(self.start.y, self.end.y)

    def xlen(self):
        return self.end.x - self.start.x

    def ylen(self):
        return self.end.y - self.start.y

    def __contains__(self, item):
        return item.xrange() in self.xrange() and item.yrange() in self.yrange()

    def __repr__(self):
        return f'Area({(self.start.x, self.end.x)}, {(self.start.y, self.end.y)}, {self.text!r})'

    def ycontains(self, area):
        return area.start.y >= self.start.y and area.end.y <= self.end.y

    def xcontains(self, area):
        return area.start.x >= self.start.x and area.end.x <= self.end.x

    def yintersects(self, area):
        r = self.yrange()
        return area.start.y in r or area.end.y in r

    def xintersects(self, area):
        r = self.xrange()
        return area.start.x in r or area.end.x in r


class LessonParser(TextArea):
    _weekpat = re.compile(r'(?P<num>[12])\s?нед\.?\s?')
    _placepat = re.compile(r'(\bа(\s|\.))?(?P<aud>\d{1,4}\s?\w?)?\s?[кК]\s?(?P<building>\d\w{0,2})')
    _halfgrouppat = re.compile(r'1/2 гр(?:\.|уппы)?')
    _typepat = re.compile(r'(КР|КП|СМ|ИМ|СГМ\s?\d)\.?\s?')
    _lengthpat = re.compile(r'(?:\(\s)?(?P<len>\d)\s?час(?:а|ов)(?:\s\))?')

    _teacherpat = re.compile(r'(?P<prof>проф|пр|ст.пр|доц|д)\.\s?(?P<lastname>\w+)\s(?P<initials>\w\.\w\.)')
    _upper = re.compile('[А-Я]')

    def parse(self):
        self.name = self.text
        self.group = None
        self.subgroup = None
        self.weekday = None

        self.time = None
        time = timepat.search(self.name)
        if time:
            self.time = time.group()
            self.sub(time)

        self.weeknum = None
        weeknum = self._weekpat.search(self.name)
        if weeknum:
            self.weeknum = weeknum.group('num')
            self.sub(weeknum)

        self.building = None
        self.auditory = None
        place = self._placepat.search(self.name)
        if place:
            self.building = place.group('building')
            self.auditory = place.group('aud')
            self.sub(place)

        self.teacher = None
        teacher = self._teacherpat.search(self.name)
        if teacher:
            self.teacher = teacher.group('lastname')
            teachers.add(self.teacher)
            self.sub(teacher)

        self.length = None
        length = self._lengthpat.search(self.name)
        if length:
            self.length = length.group('len')
            self.sub(length)

        self.ltype = None
        ltype = self._typepat.search(self.name)
        if ltype:
            self.ltype = ltype.group()
            self.sub(ltype)

        self.name = self._halfgrouppat.sub('', self.name)
        self.normalize()

        if self.name in exceptions:
            self.name = exceptions[self.name]

    def final_teacher_parse(self):
        for teacher in teachers:
            t = re.search(teacher, self.name)
            if t:
                self.teacher = t
                self.name = sub_match(t)
        self.normalize()

    def sub(self, match):
        self.name = sub_match(match)

    def normalize(self):
        self.name = normalize_spaces(self.name)

    def __repr__(self):
        attrs = [
            f'area={super().__repr__()}',
            f'text={self.text!r}',
            f'group={self.group!r}',
            f'subgroup={self.subgroup!r}',
            f'weekday={self.weekday!r}',
            f'time={self.time!r}',
            f'name={self.name!r}',
            f'teacher={self.teacher!r}',
            f'auditory={self.auditory!r}',
            f'weeknum={self.weeknum!r}',
            f'building={self.building!r}'
        ]
        s = ",\n    ".join(attrs)
        return f'LessonParser(\n    {s}\n)'


class GroupParser(TextArea):
    def parse(self):
        self.name = None
        self.dep_num = self.text[0:3]
        self.spec_num = self.text[3:6]
        self.year = self.text[6:8]


class DayParser(TextArea):
    def parse(self):
        self.times = {}


class TimeParser(TextArea):
    def parse(self):
        t = fulltimepat.fullmatch(self.text)
        self.tstart = t.group('start')
        self.tend = t.group('end')


class SheetParser:
    _grouppat = re.compile(r'\d{8}')  # (\(\d\))?

    def __init__(self, sheet, book):
        self.cells = list(sheet.get_rows())
        self._sheet = sheet
        self._book = book
        self.name = sheet.name

        self._days_headers = []
        self._time_headers = []
        self._groups = {}
        self._weekdays = {}
        self._title = None

        self.broken_lessons = []

    def cell_borders(self, cell):
        if cell is None:
            return Borders()
        b = self._book.xf_list[cell.xf_index].border
        return Borders(
            b.top_line_style, b.left_line_style,
            b.bottom_line_style, b.right_line_style,
        )

    def slice(self, start, end=None):
        end = Point(self._sheet.ncols, self._sheet.nrows) if end is None else end
        for y in range(start.y, end.y):
            yield self._sheet.row_slice(y, start.x, end.x)

    def is_dayheader(self, area):
        return area.text.lower() == 'дни'

    def is_timeheader(self, area):
        return area.text.lower() == 'часы'

    def is_day(self, area):
        isday = any(h.xcontains(area) for h in self._days_headers) or area.text in daynames
        if isday:
            daynames.add(area.text)
        return isday

    def is_time(self, area):
        # return any(h.xcontains(area) for h in self._time_headers)
        return fulltimepat.fullmatch(area.text)

    def is_group(self, area):
        return any(h.ycontains(area) for h in self._days_headers) and self._grouppat.match(area.text)

    def is_title(self, area):
        return any(h.ycontains(area) for h in self._days_headers) and not self._grouppat.match(area.text)

    def add_timeheader(self, area):
        for day in self._weekdays.values():
            if day.ycontains(area):
                time = TimeParser.copy_area(area)
                day.times[time.tstart] = time

    def set_lesson_group(self, lesson):
        for groupcell in self._groups.values():
            if groupcell.xintersects(lesson):
                lesson.group = groupcell
                break

    def set_lesson_weekday(self, lesson):
        for daycell in self._weekdays.values():
            if daycell.ycontains(lesson):
                lesson.weekday = daycell
                break

    def set_lesson_subgroup(self, lesson):
        if lesson.xlen() == 4:
            lesson.subgroup = None

    def set_lesson_weeknum(self, lesson):
        if lesson.ylen() == 4 and not lesson.weeknum:
            lesson.weeknum = None

    def set_lesson_time(self, lesson):
        if lesson.time or \
                lesson.weekday is None or \
                lesson.weekday.text not in self._weekdays:
            return
        day = self._weekdays[lesson.weekday.text]
        for timecell in day.times.values():
            if timecell.ycontains(lesson):
                lesson.time = timecell.tstart
                break

    def areas(self):
        sheet = self._sheet
        for y, row in enumerate(self.cells):
            for x, cell in enumerate(row):
                b = self.cell_borders(cell)
                if x == 0:
                    b.left = True
                if y == 0:
                    b.top = True
                if b.top and b.left:
                    start = Point(x, y)
                    end = Point(None, None)

                    xiter = zip_longest(sheet.row_slice(y, start.x, sheet.ncols),
                                        sheet.row_slice(y, start.x+1, sheet.ncols))
                    for i, (firstcell, nextcell) in enumerate(xiter):
                        fb = self.cell_borders(firstcell)
                        nb = self.cell_borders(nextcell)
                        if fb.right or nb.left:
                            end.x = x + i + 1
                            break

                    yiter = zip_longest(sheet.col_slice(x, start.y, sheet.nrows),
                                        sheet.col_slice(x, start.y+1, sheet.nrows))
                    for i, (firstcell, nextcell) in enumerate(yiter):
                        fb = self.cell_borders(firstcell)
                        nb = self.cell_borders(nextcell)
                        if fb.bottom or nb.top:
                            end.y = y + i + 1
                            break

                    if end:
                        area = TextArea(start, end)
                        area.set_cells(self)
                        yield area

    def lessons(self):
        for area in self.areas():
            if area.text:
                if self.is_dayheader(area):
                    self._days_headers.append(area)
                elif self.is_timeheader(area):
                    self._time_headers.append(area)
                elif self.is_day(area):
                    self._weekdays[area.text] = DayParser.copy_area(area)
                elif self.is_group(area):
                    self._groups[area.text] = GroupParser.copy_area(area)
                elif self.is_time(area):
                    self.add_timeheader(area)
                elif self.is_title(area):
                    self._title = area
                else:
                    lesson = LessonParser.copy_area(area)
                    self.set_lesson_group(lesson)
                    self.set_lesson_subgroup(lesson)
                    self.set_lesson_weekday(lesson)
                    self.set_lesson_time(lesson)
                    yield lesson


def bntu_books():
    root = 'C:\\Users\\Lenovo\\PycharmProjects\\schedule\\data'
    paths = [
        '1krs_2sem_19-20.xls',
        '2krs_2sem_19-20.xls',
    ]
    for path in paths:
        yield xlrd.open_workbook(os.path.join(root, path), formatting_info=True)


def cprint(*args, sep=' ', end='\n'):
    print('>>> ', end='')
    print(*args, sep=sep, end=end)


def setup_teachers():
    cprint('setting up teachers')
    for i, lesson in enumerate(lessons):
        if i % 50 == 0:
            cprint(f'{i}/{len(lessons)} lessons processed')
        lesson.final_teacher_parse()


def fill_db():
    cprint('filling db')
    for lesson in lessons:
        weekday = WEEKDAYS.get_locale(long=lesson.weekday.text).num if lesson.weekday else None
        DbLesson(
            group=lesson.group.text if lesson.group else None,
            weeknum=lesson.weeknum,
            weekday=weekday,
            subgroup=lesson.subgroup,
            time=lesson.time,
            name=lesson.name,
            teacher=lesson.teacher,
            building=lesson.building,
            auditory=lesson.auditory,
        ).save()
    cprint('finished')


def main():
    cprint('started')
    for book in bntu_books():
        for sheet in book.sheets():
            sheet = SheetParser(sheet, book)
            cprint('processing', sheet.name)
            for lesson in sheet.lessons():
                lessons.append(lesson)
    fill_db()


if __name__ == '__main__':
    main()
