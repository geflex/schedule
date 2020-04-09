from bottex.messaging import Text, Color, Button
from bottex.views import View, ButtonLink, InputLink, ReLink, manager
from bottex.core.i18n import gettext as _

from models import Lang, PType
from bases import BackButton, NotChangeButton, group_fmt, time_fmt

from app import schedule, profile_settings


def bool2onoff(value):
    if value:
        return _('Вкл')
    return _('Выкл')


def ifnot(val, res):
    return res if not val else val


class BaseView(View, isbase=True):
    error_resp = Text(_('ты что-то сломал'))
    cannot_parse_resp = Text(_('нипонял('))


class EndSetup(View, isbase=True):
    success_resp = Text(_('Ура! Всё настроили.\n'
                          'Теперь ты можешь жмакать на кнопочки и смотреть расписание)'))


class MainView(BaseView):
    __viewname__ = 'main'

    links = [
        ButtonLink(_('Сегодня'), schedule.today_schedule),
        ButtonLink(_('Завтра'), schedule.tomorrow_schedule, next_line=False),
        ButtonLink(_('Неделя'), schedule.curr_week),
        ButtonLink(_('След. неделя'), schedule.next_week, next_line=False),

        ButtonLink(_('Какая неделя'), schedule.week_num),
        ButtonLink(_('Настройки'), classnames.SettingsView.switch),
    ]


class SettingsView(BaseView):
    __viewname__ = 'settings'

    def _add_notif_switcher(self, links):
        notifs_allowed = self.request.user.notifications.allowed
        if notifs_allowed:
            button = ButtonLink(_('Откл. уведомления'),
                                profile_settings.disable_notifs,
                                Text(_('Отключили')),
                                color=Color.RED)
        else:
            button = ButtonLink(_('Вкл. уведомления'),
                                profile_settings.enable_notifs,
                                Text(_('Включили')),
                                TimeSetter.switch,
                                color=Color.GREEN)
        links.append(button)

    def _add_teacher_butttons(self, links):
        links2 = [
            ButtonLink(_('Фамилия'),
                       NameSetter.switch),
            ButtonLink(_('Стать студентом'),
                       profile_settings.ptype_setter(PType.student),
                       Text(_('Теперь ты студент')),
                       SettingsView.switch),
        ]
        links.extend(links2)

    def _add_student_buttons(self, links):
        links2 = [
            ButtonLink(_('Группа'),
                       GroupSetter.switch),
            ButtonLink(_('Подгруппа'),
                       SubgroupSetter.switch, next_line=False),
            ButtonLink(_('Стать преподом'),
                       profile_settings.ptype_setter(PType.teacher),
                       Text(_('Теперь ты препод')),
                       SettingsView.switch),
        ]
        links.extend(links2)

    @property
    def links(self):
        links = []
        self._add_notif_switcher(links)
        links.append(ButtonLink(_('Время'), TimeSetter.switch, next_line=False))

        ptype = self.request.user.ptype
        if ptype == PType.student:
            self._add_student_buttons(links)
        else:
            self._add_teacher_butttons(links)

        links.append(ButtonLink(_('Язык'), classnames.LanguageSettings.switch))
        links.append(BackButton(classnames.MainView.switch))
        # links.append(ButtonLink('Начать сначала',
        #                         manager.StartProfileTypeSetter.switch,
        #                         start_message))
        return links

    @property
    def hello_resp(self):
        user = self.request.user
        _ = self.request.gettext
        spl = ': '
        rows = [_('Тип профиля') + spl + _(user.ptype.name)]
        if user.ptype == PType.student:
            group = ifnot(user.group, '')
            rows.append(_('Группа') + spl + _(group))
            subgroup = ifnot(user.subgroup, '')
            rows.append(_('Подгруппа') + spl + _(subgroup))
        else:
            name = ifnot(user.name, '')
            rows.append(_('Фамилия') + spl + _(name))

        nfs = user.notifications
        allowed = bool2onoff(nfs.allowed)

        time = f', {nfs.time:%H:%M}' if nfs.time else ''
        rows.append(_('Уведомления') + spl + _(allowed) + time)

        rows.append(_('Язык') + spl + _(user.locale.value))
        return Text('\n'.join(rows))


class LanguageSettings(BaseView):
    __viewname__ = 'language_settings'
    hello_resp = Text(_('Выбери язык из списка ниже'))
    success_resp = Text(_('Язык установили'))

    links = []
    for lang in Lang:
        b = ButtonLink(lang.value,
                       profile_settings.set_lang(lang),
                       success_resp,
                       SettingsView.switch)
        links.append(b)
    links.append(BackButton(SettingsView.switch))


class GroupSetter(BaseView):
    __viewname__ = 'group_setter'
    hello_resp = Text(_('Введи номер своей группы'))
    cannot_parse_resp = Text(_('Номер группы должен состоять из восьми цифр'))
    success_resp = Text(_('Группу установили'))

    basic_input = ReLink(group_fmt, profile_settings.set_group, success_resp, SettingsView.switch)
    idontknow = Button(_('Не знаю номер группы('))
    links = [
        idontknow,
        NotChangeButton(SettingsView.switch),
        basic_input,
    ]


class StartGroupSetter(GroupSetter):
    __viewname__ = 'start_group_setter'
    hello_resp = Text(_('Теперь введи с клавиатуры номер своей группы'))
    links = [
        GroupSetter.idontknow,
        ReLink(group_fmt, profile_settings.set_group, GroupSetter.success_resp, classnames.StartSubgroupSetter.switch),
    ]


class SubgroupSetter(BaseView):
    __viewname__ = 'subgroup_setter'
    hello_resp = Text(_('Выбери подгруппу'))
    success_resp = Text(_('Подгруппу установили'))
    links = [
        ButtonLink(_('1'), profile_settings.set_subgroup, success_resp, SettingsView.switch),
        ButtonLink(_('2'), profile_settings.set_subgroup, success_resp, SettingsView.switch, next_line=False),
        NotChangeButton(SettingsView.switch)
    ]


class StartSubgroupSetter(SubgroupSetter, EndSetup):
    __viewname__ = 'start_subgroup_setter'
    hello_resp = Text(_('И последнее. Выбери свою подгруппу'))
    links = [
        ButtonLink(_('1'), profile_settings.set_subgroup, EndSetup.success_resp, MainView.switch),
        ButtonLink(_('2'), profile_settings.set_subgroup, EndSetup.success_resp, MainView.switch, next_line=False),
    ]


class TimeSetter(BaseView):
    __viewname__ = 'time_setter'
    hello_resp = Text(_('Введи время с клавиатуры или жмакни нужную кнопочку'))
    success_resp = Text(_('Время установили'))
    cannot_parse_resp = Text(_('С форматом проблемка('))
    links = [
        Button(_('10:00')),
        Button(_('11:00'), next_line=False),
        Button(_('12:00'), next_line=False),

        Button(_('14:00')),
        Button(_('15:00'), next_line=False),
        Button(_('16:00'), next_line=False),

        Button(_('18:00')),
        Button(_('19:00'), next_line=False),
        Button(_('20:00'), next_line=False),

        NotChangeButton(SettingsView.switch),

        ReLink(time_fmt, profile_settings.set_notifs_time, success_resp, SettingsView.switch),
    ]


class NameSetter(BaseView):
    __viewname__ = 'name_setter'
    hello_resp = Text(_('Введи свою фамилию с клавиатуры'))
    success_resp = Text(_('Фамилию установили'))
    links = [
        NotChangeButton(SettingsView.switch),
        InputLink(profile_settings.set_fio, success_resp, SettingsView.switch)
    ]


class StartNameSetter(NameSetter, EndSetup):
    __viewname__ = 'start_name_setter'
    hello_resp = Text(_('Теперь введи с клавиатуры свою фамилию'))
    success_resp = EndSetup.success_resp
    links = [
        InputLink(profile_settings.set_fio, success_resp, MainView.switch)
    ]


class StartProfileTypeSetter(BaseView):
    __viewname__ = 'start_profile_type_setter'
    hello_resp = Text(_('Выбери тип профиля'))
    success_resp = Text(_('Так, тип профиля установили'))
    links = [
        ButtonLink(_('Студент'), profile_settings.ptype_setter(PType.student), success_resp, StartGroupSetter.switch),
        ButtonLink(_('Преподаватель'), profile_settings.ptype_setter(PType.teacher), success_resp, StartNameSetter.switch),
    ]


class StartView(BaseView):
    __viewname__ = 'start'
    success_resp = Text(_('Привет! Чтобы все заработало, сначала нужно кое-что настроить '
                          '(все это можно будет поменять позже в настройках)'))
    links = [
        InputLink(lambda r: None, success_resp, StartProfileTypeSetter.switch),
    ]
    buttons = [
        Button(_('Начать'))
    ]
