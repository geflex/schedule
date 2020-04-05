from . import views, links, manager
from .views import View, viewnames, classnames
from .links import AbstractLink, ButtonLink, StrictLink, ReLink, FuncLink, InputLink


@viewnames.register
def hello_world(request):
    return ('Hello, World!\n'
            'I`m Bottex :)')
