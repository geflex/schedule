from collections import defaultdict
from typing import List, Optional as Opt
from abc import ABC

import bottex
from bottex.views.links import AbstractLink
from bottex.typing import Message, Receiver
from bottex.messaging import Text, Button


class View(ABC):
    __viewname__: str

    @property
    def links(self) -> List[AbstractLink]:
        return []

    @property
    def buttons(self) -> List[List[Button]]:
        """
        Returns the buttons that will be sent
        to the user when they switch to this view.
        """
        buttons: List[List[Button]] = []
        for link in self.links:
            if isinstance(link, Button):
                if link.next_line:
                    buttons.append([link])
                else:
                    buttons[-1].append(link)
        return buttons

    hello_resp = Text('')
    success_resp = Text('')
    error_resp = Text('Error')
    cannot_parse_resp = Text('Unknown command')

    def error_handler(self, request, e) -> Message:
        return self.error_resp

    def cannot_parse_handler(self, request) -> Message:
        return self.cannot_parse_resp

    def __init_subclass__(cls, isbase=False, **kwargs):
        if not isbase:
            if '.' in cls.__viewname__:
                raise ValueError('__viewname__ must not contain dots')
            viewnames[cls.__viewname__] = cls.parse_request
            classnames[cls.__name__] = cls
            cls.logger = bottex.logging.get_logger(cls.__name__)

    def __init__(self, request):
        self.request = request

    @classmethod
    def parse_request(cls, request) -> Message:
        return cls(request)._get_response()

    @classmethod
    def switch(cls, request) -> Message:
        self = cls(request)
        self._save_state()
        response = self.hello_resp
        return response.with_buttons(self.buttons)

    def _get_response(self) -> Message:
        """
        Should parse the text message passed in request and return the response
        """
        receiver = self._get_receiver()
        try:
            response = receiver(self.request)
        except Exception as e:
            self.logger.error(e, exc_info=True)
            response = self.error_handler(self.request, e)
        return response.with_buttons(self.buttons)

    def _get_receiver(self) -> Receiver:
        """
        Returns the receiver of this view that matches current request.
        If the link does not exist, returns `self.cannot_parse_handler`
        """
        for link in self.links:
            if isinstance(link, AbstractLink) and link.match(self.request):
                return link.receiver
        return self.cannot_parse_handler

    def _save_state(self) -> None:
        """
        Saves the name of this view in the user model.
        This is necessary for the next request from the current
        user to be sent for parsing to this view.
        """
        self.request.user.current_view = self.__viewname__
        self.request.user.save()


class ViewManager(defaultdict):
    @property
    def default_view(self):
        return self.default_factory()

    @default_view.setter
    def default_view(self, func_or_cls):
        func = func_or_cls
        if issubclass(func_or_cls, View):
            func = func_or_cls.parse_request

        def factory():
            return func
        self.default_factory = factory

    def __init__(self):
        super().__init__()

    def __setitem__(self, name, cls):
        assert name not in self, f'View with name {name!r} already exists.'
        super().__setitem__(name, cls)

    def register(self, name=None):
        if name is None:
            def _reg(f):
                if hasattr(f, '__viewname__'):
                    self[f.__viewname__] = f
                else:
                    self[f.__name__] = f
        else:
            def _reg(f):
                self[name] = f

        def _register(func):
            _reg(func)
            return func
        return _register

    def copy(self):
        new = ViewManager()
        new.default_view = self.default_view
        for k, v in self.items():
            new[k] = v
        return new


viewnames = ViewManager()
classnames = ViewManager()


def set_default_view(func_or_cls):
    viewnames.default_view = func_or_cls
