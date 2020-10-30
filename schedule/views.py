from models import Lang, PType
from bases import group_fmt, time_fmt


def bool2onoff(value):
    if value:
        return 'Вкл'
    return 'Выкл'


def ifnot(val, res):
    return res if not val else val


class BaseView:
    error = 'ты что-то сломал'
    cannot_parse = 'нипонял('


class EndSetup:
    success = ('Ура! Всё настроили.\n'
               'Теперь ты можешь жмакать на кнопочки и смотреть расписание)')


class MainView(BaseView):
    __viewname__ = 'main'

    links = [
        'Сегодня', 'Завтра',
        'Неделя', 'След. неделя',
        'Какая неделя',
        'Настройки',
    ]


class SettingsView(BaseView):
    __viewname__ = 'settings'

    def _add_notif_switcher(self, links):
        notifs_allowed = self.request.user.notifications.allowed
        if notifs_allowed:
            button = ('Откл. уведомления',
                      profile_settings.disable_notifs,
                      Text(_('Отключили')),
                      color=Color.RED)
        else:
            button = ('Вкл. уведомления',
                      profile_settings.enable_notifs,
                      Text('Включили'),
                      TimeSetter.switch,
                      color=Color.GREEN)
        links.append(button)

    def _add_teacher_butttons(self, links):
        links2 = [
            ButtonLink('Фамилия',
                       NameSetter.switch),
            ButtonLink('Стать студентом',
                       profile_settings.ptype_setter(PType.student),
                       Text('Теперь ты студент'),
                       SettingsView.switch),
        ]
        links.extend(links2)

    def _add_student_buttons(self, links):
        links2 = [
            ButtonLink('Группа',
                       GroupSetter.switch),
            ButtonLink('Подгруппа',
                       SubgroupSetter.switch, next_line=False),
            ButtonLink('Стать преподом',
                       profile_settings.ptype_setter(PType.teacher),
                       'Теперь ты препод',
                       SettingsView.switch),
        ]
        links.extend(links2)

    @property
    def links(self):
        links = []
        self._add_notif_switcher(links)
        links.append('Время', TimeSetter.switch, next_line=False)

        ptype = self.request.user.ptype
        if ptype == PType.student:
            self._add_student_buttons(links)
        else:
            self._add_teacher_butttons(links)

        links.append('Язык', tests_.test_app.router.router.switch)
        links.append(tests_.test_app.router.router.switch)
        # links.append(ButtonLink('Начать сначала',
        #                         manager.StartProfileTypeSetter.switch,
        #                         start_message))
        return links

    @property
    def hello_resp(self):
        user = self.request.user
        _ = self.request.gettext
        spl = ': '
        rows = ['Тип профиля' + spl + _(user.ptype.name)]
        if user.ptype == PType.student:
            group = ifnot(user.group, '')
            rows.append('Группа' + spl + _(group))
            subgroup = ifnot(user.subgroup, '')
            rows.append('Подгруппа' + spl + _(subgroup))
        else:
            name = ifnot(user.name, '')
            rows.append('Фамилия' + spl + _(name))

        nfs = user.notifications
        allowed = bool2onoff(nfs.allowed)

        time = f', {nfs.time:%H:%M}' if nfs.time else ''
        rows.append('Уведомления' + spl + _(allowed) + time)

        rows.append('Язык' + spl + _(user.locale.value))
        return '\n'.join(rows)


class LanguageSettings(BaseView):
    __viewname__ = 'language_settings'
    hello = 'Выбери язык из списка ниже'
    success = 'Язык установили'

    links = []
    for lang in Lang:
        b = ButtonLink(lang.value,
                       profile_settings.set_lang(lang),
                       success,
                       SettingsView.switch)
        links.append(b)
    links.append(BackButton(SettingsView.switch))


class GroupSetter(BaseView):
    __viewname__ = 'group_setter'
    hello = 'Введи номер своей группы'
    cannot_parse = 'Номер группы должен состоять из восьми цифр'
    success = 'Группу установили'

    basic_input = ReLink(group_fmt, profile_settings.set_group, success, SettingsView.switch)
    idontknow = 'Не знаю номер группы('
    links = [
        idontknow,
        NotChangeButton(SettingsView.switch),
        basic_input,
    ]


class StartGroupSetter(GroupSetter):
    __viewname__ = 'start_group_setter'
    hello = 'Теперь введи с клавиатуры номер своей группы'
    links = [
        GroupSetter.idontknow,
        (group_fmt, profile_settings.set_group, GroupSetter.success, tests_.test_app.router.router.switch),
    ]


class SubgroupSetter(BaseView):
    __viewname__ = 'subgroup_setter'
    hello = 'Выбери подгруппу'
    success = 'Подгруппу установили'
    links = [
        ('1', profile_settings.set_subgroup, success, SettingsView.switch),
        ('2', profile_settings.set_subgroup, success, SettingsView.switch, next_line=False),
        NotChangeButton(SettingsView.switch)
    ]


class StartSubgroupSetter(SubgroupSetter, EndSetup):
    __viewname__ = 'start_subgroup_setter'
    hello = 'И последнее. Выбери свою подгруппу'
    links = [
        ('1', profile_settings.set_subgroup, EndSetup.success, MainView.switch),
        ('2', profile_settings.set_subgroup, EndSetup.success, MainView.switch, next_line=False),
    ]


class TimeSetter(BaseView):
    __viewname__ = 'time_setter'
    hello = 'Введи время с клавиатуры или жмакни нужную кнопочку'
    success = 'Время установили'
    cannot_parse = 'С форматом проблемка('
    links = [
        '10:00',
        '11:00',
        '12:00',

        '14:00',
        '15:00',
        '16:00',

        '18:00',
        '19:00',
        '20:00',

        NotChangeButton(SettingsView.switch),
        ReLink(time_fmt, profile_settings.set_notifs_time, success, SettingsView.switch),
    ]


class NameSetter(BaseView):
    __viewname__ = 'name_setter'
    hello = 'Введи свою фамилию с клавиатуры'
    success = 'Фамилию установили'
    links = [
        NotChangeButton(SettingsView.switch),
        InputLink(profile_settings.set_fio, success, SettingsView.switch)
    ]


class StartNameSetter(NameSetter, EndSetup):
    __viewname__ = 'start_name_setter'
    hello = 'Теперь введи с клавиатуры свою фамилию'
    success = EndSetup.success
    links = [
        InputLink(profile_settings.set_fio, success, MainView.switch)
    ]


class StartProfileTypeSetter(BaseView):
    __viewname__ = 'start_profile_type_setter'
    hello = 'Выбери тип профиля'
    success = 'Так, тип профиля установили'
    links = [
        ('Студент', profile_settings.ptype_setter(PType.student), success, StartGroupSetter.switch),
        ('Преподаватель', profile_settings.ptype_setter(PType.teacher), success, StartNameSetter.switch),
    ]


class StartView(BaseView):
    __viewname__ = 'start'
    success = ('Привет! Чтобы все заработало, сначала нужно кое-что настроить '
               '(все это можно будет поменять позже в настройках)')
    links = [
        (return_none, success, StartProfileTypeSetter.switch),
    ]
    buttons = [
        'Начать'
    ]


class DepartmentGroups(BaseView):
    __viewname__ = 'department_groups'


class Departments(BaseView):
    __viewname__ = 'departments'
