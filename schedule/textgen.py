import random
from bottex.core.i18n import gettext as _


def axaxax(limit=10):
    ax = _('ах'), _('пх')
    s = random.choices(ax, k=limit)
    if s not in ax:
        return ''.join(s)
    return ''


def positive_scopes(limit=3):
    n = random.randint(0, limit)
    return ')'*n


def repeat(request):
    axax = axaxax()
    axax += ' ' if axax else ''
    scopes = positive_scopes(4)
    return axax + request.msg.lower() + scopes


def too_big_msg(request):
    return ['онет', 'слишком много читать(']
