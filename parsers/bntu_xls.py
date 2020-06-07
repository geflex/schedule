import re  # модуль регулярных выражений
import os  # для объединения путей
from itertools import zip_longest, chain  # утилиты для итерирования
from collections import namedtuple

import xlrd  # библиотека для работы с excel
from mongoengine.connection import _get_db  # для доступа к соединению с базой

from models import Lesson as DbLesson  # импортируем нашу модель


WEEKDAYS = [
    'понедельник',
    'вторник',
    'среда',
    'четверг',
    'пятница',
    'суббота',
]


_many_spaces = re.compile(r'\s+')
def normalize_spaces(s):
    """Удаляет ненужные пробелы"""
    return _many_spaces.sub(' ', s).strip()


def del_match(m):
    """Удаляет совпадение из строки"""
    return m.string[:m.start()] + m.string[m.end():]


class MatchWrapper:
    def __init__(self, m):
        self.m = m

    def group(self, name=None):
        if self.m is not None:
            if name is None:
                return self.m.group()
            return self.m.group(name)
        else:
            return None


class CellWrapper:
    def __init__(self, cell):
        self.cell = cell

    def search(self, pat):
        m = pat.search(self.cell.value)
        if m:
            self.cell.value = del_match(m)
        return MatchWrapper(m)


class Borders:
    """Хранит информацию о границах"""
    def __init__(self, top=False, left=False, bottom=False, right=False):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    def confined(self):
        """"""
        return all([self.top, self.left, self.bottom, self.right])

    def __repr__(self):
        return f'Borders({self.top}, {self.left}, {self.bottom}, {self.right})'


Point = namedtuple('Point', 'x, y')
def __point_bool(self):
    return bool(self.x and self.y)
Point.__bool__ = __point_bool


class BaseArea:
    """Прямоугольная область из нескольких ячеек"""
    @property
    def cells(self):
        return self._cells

    @property
    def text(self):
        if self._text is None:
            self.regen_text()
        return self._text

    def regen_text(self):
        text = []
        for row in self._cells:
            for cell in row:
                text.append(cell.value)
        text = ' '.join(text)
        self._text = normalize_spaces(text)
        return self._text

    def __init__(self, start, end, cells=None):
        self.start = start  # type: Point
        self.end = end  # type: Point
        self._cells = list(cells) if cells is not None else []
        self._strip_cells()
        self._text = None
        self.parse()

    @classmethod
    def init_from(cls, area: 'BaseArea'):
        """Инициализирует объект класса, копируя основные свойства area"""
        obj = cls(area.start, area.end, area._cells)
        obj._text = area._text
        return obj

    def _strip_cells(self):
        for cell in chain(*self._cells):
            if isinstance(cell.value, float):
                cell.value = int(cell.value)
            if cell.value:
                cell.value = str(cell.value).strip()

    def parse(self):
        """Че-то парсит и инициализирует объект"""
        pass

    def xrange(self):
        return range(self.start.x, self.end.x)

    def yrange(self):
        return range(self.start.y, self.end.y)

    def xlen(self):
        return self.end.x - self.start.x

    def ylen(self):
        return self.end.y - self.start.y

    def __contains__(self, item: "BaseArea"):
        return item.xrange() in self.xrange() and item.yrange() in self.yrange()

    def __repr__(self):
        return f'Area({(self.start.x, self.end.x)}, {(self.start.y, self.end.y)}, {self.text!r})'

    def ycontains(self, area: "BaseArea"):
        """Входит ли область area в эту область по оси y"""
        return area.start.y >= self.start.y and area.end.y <= self.end.y

    def xcontains(self, area: "BaseArea"):
        """Входит ли область area в эту область по оси x"""
        return area.start.x >= self.start.x and area.end.x <= self.end.x

    def yintersects(self, area: "BaseArea"):
        """Пересекается ли эта область с областью area по оси y"""
        r = self.yrange()
        return area.start.y in r or area.end.y in r

    def xintersects(self, area: "BaseArea"):
        """Пересекается ли эта область с областью area по оси x"""
        r = self.xrange()
        return area.start.x in r or area.end.x in r


re_time = re.compile(r'([0-1]?\d|2[0-3])\.[0-5]\d')
re_fulltime = re.compile(fr'(?P<start>{re_time.pattern})\s?-\s?(?P<end>{re_time.pattern})')
re_group = re.compile(r'\d{8}')  # (\(\d\))?

re_week = re.compile(r'\b(?P<num>[12])\s?нед\.?')
re_building = re.compile(r'\b[кК]\s*'
                         r'(?P<b>\d\w{0,2})')
re_auditory = re.compile(r'\b(?:[ал]\.?\s?)?'
                         r'(?P<a>\d{1,4}\s*\w?\b)')
re_halfgroup = re.compile(r'\b1/2 гр(?:\.|уппы)?')
re_type = re.compile(r'\b(КР|КП|СМ|ИМ|СГМ\s?\d)\.?\s?')
re_length = re.compile(r'\b(?:\(\s)?(?P<len>\d)\s?час(?:а|ов)(?:\s\))?')
re_teacher = re.compile(r'\b'
                        r'('
                            r'(?P<prof>(?:проф|пр|ст\.пр|доц|д)\.)\s*'
                            r'(?P<lastname>\w+)\s*'
                            r'(?P<initials>(?:[А-Я]\.){2})?'
                        r'|'
                            r'(?P<lastname2>\w+)\s*'
                            r'(?P<initials2>(?:[А-Я]\.){2})'
                        r')')

# отдельный случай
exceptions = {
    'ф и з и ч е с к а я к у л ь т у р а': 'Физическая культура'
}


class LessonArea(BaseArea):
    @property
    def doc(self):
        if not hasattr(self, '_doc'):
            self._doc = DbLesson(
                group=self.group,
                weeknum=self.weeknum,
                weekday=self.weekday,
                subgroup=self.subgroup,
                time=self.time,
                name=self.name,
                teachers=self.teachers,
                building=self.building,
                auditories=self.auditories,
            )
        return self._doc

    def parse(self):
        self.name = None
        self.group = None
        self.subgroup = None
        self.weekday = None
        self.time = None
        self.weeknum = None
        self.building = None
        self.auditories = []
        self.teachers = []
        self.lenght = None

        for cell in chain(*self.cells):
            if cell.value:
                cell = CellWrapper(cell)
                if not self.time:
                    self.time = cell.search(re_time).group()

                halfgroup = cell.search(re_halfgroup).group()
                if halfgroup and not self.subgroup:
                    self.subgroup = 1

                if not self.lenght:
                    self.lenght = cell.search(re_length).group('len')

                weeknum = cell.search(re_week).group('num')
                if not self.weeknum:
                    self.weeknum = weeknum

                if not self.building:
                    self.building = cell.search(re_building).group('b')

                while True:
                    auditory = cell.search(re_auditory).group('a')
                    if auditory:
                        self.auditories.append(auditory)
                    else:
                        break
                while True:
                    m = cell.search(re_teacher)
                    teacher = m.group('lastname') or m.group('lastname2')
                    if teacher:
                        self.teachers.append(teacher)
                    else:
                        break

        self.name = normalize_spaces(self.regen_text())
        if self.name in exceptions:
            self.name = exceptions[self.name]

    def __repr__(self):
        attrs = [
            f'area={super().__repr__()}',
            f'text={self.text!r}',
            f'group={self.group!r}',
            f'subgroup={self.subgroup!r}',
            f'weekday={self.weekday!r}',
            f'time={self.time!r}',
            f'lenght={self.lenght!r}'
            f'name={self.name!r}',
            f'teacher={self.teachers!r}',
            f'auditory={self.auditories!r}',
            f'weeknum={self.weeknum!r}',
            f'building={self.building!r}'
        ]
        s = ",\n    ".join(attrs)
        return f'LessonArea(\n    {s}\n)'


class TimeArea(BaseArea):
    def parse(self):
        t = re_fulltime.fullmatch(self.text)
        self.tstart = t.group('start')
        self.tend = t.group('end')


class SheetParser:
    def __init__(self, sheet, book):
        self._cells = list(sheet.get_rows())
        self._sheet = sheet
        self._book = book
        self.name = sheet.name

        self._curr_header = None
        self._title = None
        self._group_areas = {}
        self._curr_weekday = None
        self._curr_time = None

        self.broken_lessons = []

    def slice(self, start: Point, end: Point = None):
        """Возвращает двумерный срез ячеек листа"""
        end = Point(self._sheet.ncols, self._sheet.nrows) if end is None else end
        for y in range(start.y, end.y):
            yield self._sheet.row_slice(y, start.x, end.x)

    def is_day(self, area):
        """Является ли область ячеек днем недели"""
        return area.text in WEEKDAYS

    def is_time(self, area):
        """Является ли область"""
        return re_fulltime.fullmatch(area.text)

    def is_group(self, area):
        return self._curr_header.end.y == area.end.y and re_group.match(area.text)

    def is_title(self, area):
        return self._curr_header.start.y == area.start.y and not re_group.match(area.text)

    def _set_lesson_group(self, lesson):
        for group in self._group_areas.values():
            if group.xintersects(lesson):
                self._curr_group = group
                lesson.group = group.text
                break

    def _set_lesson_subgroup(self, lesson):
        if self._curr_group:
            if lesson.xlen() < self._curr_group.xlen():
                if lesson.start.x == self._curr_group.start.x:
                    lesson.subgroup = 1
                elif lesson.end.x == self._curr_group.end.x:
                    lesson.subgroup = 2

    def _set_lesson_weekday(self, lesson):
        if self._curr_weekday:
            wd = self._curr_weekday.text
            lesson.weekday = WEEKDAYS.index(wd)

    def _set_lesson_time(self, lesson):
        if self._curr_time and not lesson.time:
            lesson.time = self._curr_time.tstart

    def _set_lesson_weeknum(self, lesson):
        if self._curr_time:
            if lesson.ylen() < self._curr_time.ylen():
                if lesson.start.y == self._curr_time.start.y:
                    lesson.weeknum = '1'
                elif lesson.end.y == self._curr_time.end.y:
                    lesson.weeknum = '2'

    def cell_borders(self, cell):
        if cell is None:
            return Borders()
        b = self._book.xf_list[cell.xf_index].border  # получаем стили ячейки
        return Borders(
            b.top_line_style, b.left_line_style,
            b.bottom_line_style, b.right_line_style,
        )

    def areas(self):
        sheet = self._sheet  # сокращение для удобства
        for y, row in enumerate(self._cells):  # для каждой строки с координатой y
            for x, cell in enumerate(row):  # для каждой ячейки с координатой x в строке
                b = self.cell_borders(cell)  # получаем границы ячейки
                if x == 0:  # край листа тоже считаем границой
                    b.left = True
                if y == 0:
                    b.top = True

                if b.top and b.left:  # если ячейка в левом верхнем углу имеет границы
                    start = Point(x, y)  # задаем точку старта
                    end = Point(None, None)  # и еще неизвестную точку конца

                    # ищем конечную точку по оси x
                    xiter = zip_longest(sheet.row_slice(y, start.x, sheet.ncols),
                                        sheet.row_slice(y, start.x + 1, sheet.ncols))
                    for i, (firstcell, nextcell) in enumerate(xiter):
                        fb = self.cell_borders(firstcell)
                        nb = self.cell_borders(nextcell)
                        if fb.right or nb.left:
                            end.x = x + i + 1
                            break

                    # ищем конечную точку по оси y
                    yiter = zip_longest(sheet.col_slice(x, start.y, sheet.nrows),
                                        sheet.col_slice(x, start.y + 1, sheet.nrows))
                    for i, (firstcell, nextcell) in enumerate(yiter):
                        fb = self.cell_borders(firstcell)
                        nb = self.cell_borders(nextcell)
                        if fb.bottom or nb.top:
                            end.y = y + i + 1
                            break

                    if end:  # если конечная точка найдена
                        cells = list(self.slice(start, end))
                        area = BaseArea(start, end, cells)
                        yield area

    def lessons(self):
        for area in self.areas():
            if area.text:
                if area.text.lower() in ('дни', 'часы'):
                    self._curr_header.append(area)

                elif self.is_title(area):
                    self._title = area

                elif self.is_group(area):
                    self._group_areas[area.text] = area

                elif self.is_day(area):
                    self._curr_weekday = area

                elif self.is_time(area):
                    area = TimeArea.init_from(area)
                    self._curr_time = area

                else:
                    lesson = LessonArea.init_from(area)
                    self._set_lesson_group(lesson)
                    self._set_lesson_weekday(lesson)
                    self._set_lesson_time(lesson)
                    self._set_lesson_subgroup(lesson)
                    self._set_lesson_weeknum(lesson)
                    yield lesson


def setup_teachers():
    print('setting up teachers')
    teachers = set(DbLesson.objects().distinct('teacher'))
    lessons = list(DbLesson.objects())  # для использования len
    for i, lesson in enumerate(lessons):
        for teacher in teachers:  # set нельзя изменять во время итерации
            lesson.teacher = lesson.sub(teacher).group()
            lesson.normalize()

        if i % 50 == 0:
            print(f'{i}/{len(lessons)} lessons processed')


def bntu_books():
    root = 'C:\\Users\\Lenovo\\PycharmProjects\\schedule\\data'  # папка с документами
    paths = [  # Пути к документам
        '1krs_2sem_19-20.xls',
        '2krs_2sem_19-20.xls',
    ]
    for path in paths:  # поочередно открываем документы
        yield xlrd.open_workbook(os.path.join(root, path), formatting_info=True)


def main():
    print('started')
    for book in bntu_books():
        for sheet in book.sheets():
            sheet = SheetParser(sheet, book)
            print('processing', sheet.name)
            for lesson in sheet.lessons():
                lesson.doc.save()


if __name__ == '__main__':
    _get_db().drop_collection('lessons')
    main()
