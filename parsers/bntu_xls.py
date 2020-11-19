import os
import re
from itertools import zip_longest, chain
from typing import Match

import xlrd

from schedule import models

WEEKDAYS = [
    'понедельник',
    'вторник',
    'среда',
    'четверг',
    'пятница',
    'суббота',
]


re_multispace = re.compile(r'\s+')
def normalize_spaces(s):
    """Удаляет ненужные пробелы"""
    return re_multispace.sub(' ', s).strip()


def del_match(m: Match):
    """Удаляет совпадение из строки"""
    return m.string[:m.start()] + m.string[m.end():]


class Borders:
    """Хранит информацию о границах"""
    def __init__(self, top=False, left=False, bottom=False, right=False):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    def __repr__(self):
        return f'Borders({self.top}, {self.left}, {self.bottom}, {self.right})'


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __bool__(self):
        return None not in (self.x, self.y)

    def __repr__(self):
        return f'Point({self.x}, {self.y})'


class BaseArea:
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
    def init_from(cls, area: 'BaseArea') -> 'BaseArea':
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
        """Для подклассов"""
        pass

    def xrange(self):
        return range(self.start.x, self.end.x)

    def yrange(self):
        return range(self.start.y, self.end.y)

    def xlen(self):
        return self.end.x - self.start.x

    def ylen(self):
        return self.end.y - self.start.y

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

    def __repr__(self):
        return f'Area({(self.start.x, self.end.x)}, {(self.start.y, self.end.y)}, {self.text!r})'


class MatchWrapper:
    def __init__(self, m):
        self.m = m

    def group(self, *args, **kwargs):
        if self.m:
            return self.m.group(*args, **kwargs)
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

exceptions = {
    'ф и з и ч е с к а я к у л ь т у р а': 'Физическая культура'
}


class LessonArea(BaseArea):
    def save(self):
        lesson = models.Lesson()
        lesson.weeknum = self.weeknum
        lesson.weekday = self.weekday
        lesson.subgroup = self.subgroup
        lesson.time = self.time
        lesson.name = self.name

        building = models.Building(name=self.building)

        lesson.groups = [models.Group(name=g) for g in self.groups]
        lesson.teachers = [models.Teacher(last_name=name) for name in self.teachers]
        lesson.places = [models.Place(building=building, auditory=a) for a in self.auditories]

        lesson.session.add(lesson)
        lesson.sessiion.commit()

    def parse(self):
        self.name = None  # строка, которая останется после удаления совпадений
        self.groups = []  # номера групп
        self.subgroup = None  # номер подгруппы
        self.weekday = None  # день недели
        self.time = None  # время начала занятия
        self.weeknum = None  # номер недели
        self.building = None  # корпус
        self.auditories = []  # аудитории
        self.teachers = []  # преподаватели
        self.lenght = None  # длительность занятия

        for cell in chain(*self.cells):  # для каждой ячейки
            if cell.value:  # если ячейка не пустая
                cell = CellWrapper(cell)  # оборачиваем ячейку для удобства
                if not self.time:  # если время начала данного занятия еще не найдено
                    self.time = cell.search(re_time).group()  # находим его

                halfgroup = cell.search(re_halfgroup).group()
                if halfgroup and not self.subgroup:
                    self.subgroup = 1  # номер подгруппы обычно не указан явно в тексте

                if not self.lenght:  # длительность занятия
                    self.lenght = cell.search(re_length).group('len')

                if not self.weeknum:  # номер недели
                    self.weeknum = cell.search(re_week).group('num')

                if not self.building:  # корпус
                    self.building = cell.search(re_building).group('b')

                while True:  # ищем все упоминания аудиторий
                    auditory = cell.search(re_auditory).group('a')
                    if auditory:
                        self.auditories.append(auditory)
                    else:
                        break
                while True:  # ищем все упоминания учителей
                    m = cell.search(re_teacher)
                    teacher = m.group('lastname') or m.group('lastname2')
                    if teacher:
                        self.teachers.append(teacher)
                    else:
                        break
        # оставшийся текст будет названием занятия
        self.name = normalize_spaces(self.regen_text())
        if self.name in exceptions:  # проверяем исключительные случаи
            self.name = exceptions[self.name]  # заменяем

    def __repr__(self):
        attrs = [
            f'area={super().__repr__()}',
            f'text={self.text!r}',
            f'group={self.groups!r}',
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


class BaseSheetParser:
    def __init__(self, sheet, book):
        self._cells = list(sheet.get_rows())  # ячейки листа
        self._sheet = sheet
        self._book = book
        self.name = sheet.name  # название листа

    def get_cell_borders(self, cell):
        if cell is None:
            # noinspection PyArgumentList
            return Borders()
        b = self._book.xf_list[cell.xf_index].border  # получаем стили ячейки
        return Borders(
            b.top_line_style, b.left_line_style,
            b.bottom_line_style, b.right_line_style,
        )

    def get_area(self, start: Point, end: Point = None):
        end = Point(self._sheet.ncols, self._sheet.nrows) if end is None else end
        cells = []
        for y in range(start.y, end.y):
            cells.append(self._sheet.row_slice(y, start.x, end.x))
        return BaseArea(start, end, cells)

    def get_areas(self):
        sheet = self._sheet  # сокращение для удобства
        for y, row in enumerate(self._cells):  # для каждой строки с координатой y
            for x, cell in enumerate(row):  # для каждой ячейки с координатой x в строке
                b = self.get_cell_borders(cell)  # получаем границы ячейки
                if x == 0:  # края листа тоже считаем границоми
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
                        fb = self.get_cell_borders(firstcell)
                        nb = self.get_cell_borders(nextcell)
                        if fb.right or nb.left:
                            end.x = x + i + 1
                            break

                    # ищем конечную точку по оси y
                    yiter = zip_longest(sheet.col_slice(x, start.y, sheet.nrows),
                                        sheet.col_slice(x, start.y + 1, sheet.nrows))
                    for i, (firstcell, nextcell) in enumerate(yiter):
                        fb = self.get_cell_borders(firstcell)
                        nb = self.get_cell_borders(nextcell)
                        if fb.bottom or nb.top:
                            end.y = y + i + 1
                            break

                    if end:  # если конечная точка найдена
                        area = self.get_area(start, end)  # создаем объект BaseArea
                        yield area  # передаем area в место вызова


class SheetParser(BaseSheetParser):
    def __init__(self, sheet, book):
        super().__init__(sheet, book)
        self._curr_header = None
        self._title = None
        self._group_areas = []
        self._curr_weekday = None
        self._curr_time = None
        self._curr_group = None

    def _is_day(self, area: BaseArea):
        return area.text in WEEKDAYS

    def _is_time(self, area: BaseArea):
        return re_fulltime.fullmatch(area.text)

    def _is_group(self, area: BaseArea):
        return self._curr_header.end.y == area.end.y and re_group.match(area.text)

    def _is_title(self, area: BaseArea):
        return self._curr_header.start.y == area.start.y and not re_group.match(area.text)

    def _set_lesson_group(self, lesson):
        """Добавляет все блоки групп, пересекающиеся с lesson по оси x"""
        for group_area in self._group_areas:
            if group_area.xintersects(lesson):
                self._curr_group = group_area
                lesson.groups.append(group_area.text)

    def _set_lesson_subgroup(self, lesson: LessonArea):
        """Устанавливает номер подгруппы объекта lesson"""
        # если ни одна группа не определена, то и _curr_group, соответственно, тоже
        if lesson.groups:
            # если по оси x длина блока меньше чем длина блока с группой
            if lesson.xlen() < self._curr_group.xlen():
                # находится ли блок слева
                if lesson.start.x == self._curr_group.start.x:
                    lesson.subgroup = 1
                # или справа
                elif lesson.end.x == self._curr_group.end.x:
                    lesson.subgroup = 2

    def _set_lesson_weekday(self, lesson: LessonArea):
        """Устанавливает номер дня недели объекта lesson"""
        if self._curr_weekday:
            wd = lesson.text
            lesson.weekday = WEEKDAYS.index(wd)

    def _set_lesson_time(self, lesson: LessonArea):
        """
        Устанавливает время начала занятия для lesson,
        если оно не было определено в тексте
        """
        if self._curr_time and not lesson.time:
            lesson.time = self._curr_time.tstart

    def _set_lesson_weeknum(self, lesson: LessonArea):
        """Устанавливает номер недели для lesson"""
        if self._curr_time:
            if lesson.ylen() < self._curr_time.ylen():
                # находится ли блок сверху
                if lesson.start.y == self._curr_time.start.y:
                    lesson.weeknum = '1'
                # или снизу
                elif lesson.end.y == self._curr_time.end.y:
                    lesson.weeknum = '2'

    def lessons(self):
        for area in self.get_areas():
            if area.text:
                # пытаемся узнать тип ячейки
                if area.text.lower() in ('дни', 'часы'):
                    self._curr_header = area

                elif self._is_title(area):  # ячейка с названием факультета
                    self._title = area

                elif self._is_group(area):  # ячейка с номером группы
                    self._group_areas.append(area)

                elif self._is_day(area):  # ячейка с днем недели
                    self._curr_weekday = area

                elif self._is_time(area):  # ячейка с временем занятия
                    area = TimeArea.init_from(area)
                    self._curr_time = area

                else:
                    lesson = LessonArea.init_from(area)
                    # устанавливаем атрибуты, зависящие от положения ячейки
                    self._set_lesson_group(lesson)
                    self._set_lesson_weekday(lesson)
                    self._set_lesson_time(lesson)
                    self._set_lesson_subgroup(lesson)
                    self._set_lesson_weeknum(lesson)
                    yield lesson  # передаем lesson в место вызова


def bntu_books():
    root = '.\\parsers\\data'  # папка с документами
    paths = [
        '1krs_2sem_19-20.xls',
        '2krs_2sem_19-20.xls',
    ]
    for path in paths:
        yield xlrd.open_workbook(os.path.join(root, path), formatting_info=True)


def main():
    print('started')
    for book in bntu_books():
        for sheet in book.sheets():
            sheet = SheetParser(sheet, book)
            print('processing', sheet.name)
            for lesson in sheet.lessons():
                lesson.save()


if __name__ == '__main__':
    # collection.drop()
    main()
