import datetime


def ptype_setter(t):
    def _setter(request):
        user = request.user
        user.ptype = t
        user.save()
    return _setter


def set_group(request):
    user = request.user
    user.group = request.msg.text
    user.save()


def set_subgroup(request):
    user = request.user
    user.subgroup = request.msg.text
    user.save()


def set_fio(request):
    user = request.user
    user.name = request.msg.text
    user.save()


def set_lang(lang):
    def _setter(request):
        user = request.user
        user.locale = lang
        user.save()
    return _setter


def enable_notifs(request):
    request.user.notifications.allowed = True
    request.user.save()


def disable_notifs(request):
    request.user.notifications.allowed = False
    request.user.save()


def set_notifs_time(request):
    p = request.parsed
    hour, minute = int(p.group('hour')), int(p.group('minute'))
    request.user.notifications.time = datetime.time(hour, minute)
    request.user.save()
