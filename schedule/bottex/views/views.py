from typing import List
from abc import ABC

import bottex
from bottex.views.links import AbstractLink
from bottex.drivers import Message, Text, Button, Handler
from bottex.utils.manager import NameManager
from bottex.utils.lazy import Unloaded


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
            if not isinstance(cls.__viewname__, str):
                raise TypeError('__viewname__ must be str')
            viewnames[cls.__viewname__] = cls.handle
            classnames[cls.__name__] = cls

    def __init__(self, request):
        self.request = request

    @classmethod
    def handle(cls, request) -> Message:
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
        handler = self._get_handler()
        try:
            response = handler(self.request)
        except Exception as e:
            bottex.logger.error(e, exc_info=True)
            response = self.error_handler(self.request, e)
        return response.with_buttons(self.buttons)

    def _get_handler(self) -> Handler:
        """
        Returns the handler of this view that matches current request.
        If the link does not exist, returns `self.cannot_parse_handler`
        """
        for link in self.links:
            if isinstance(link, AbstractLink) and link.match(self.request):
                return link.handler
        return self.cannot_parse_handler

    def _save_state(self) -> None:
        """
        Saves the name of this view in the user model.
        This is necessary for the next request from the current
        user to be sent for parsing to this view.
        """
        self.request.user.last_view = self.__viewname__
        self.request.user.save()


class ViewManager(NameManager):
    @property
    def default_view(self):
        return self.default_factory()

    @default_view.setter
    def default_view(self, func_or_cls):
        func = func_or_cls
        if issubclass(func_or_cls, View):
            func = func_or_cls.handle

        def factory():
            return func
        self.default_factory = factory

    def __setitem__(self, name, cls):
        assert name not in self, f'View with name {name!r} already exists.'
        super().__setitem__(name, cls)

    def __getitem__(self, name):
        try:
            return super().__getitem__(name)
        except KeyError:
            return Unloaded(name, self)

    __getattr__ = __getitem__


viewnames = ViewManager()
classnames = ViewManager()


def set_default_view(func_or_cls):
    viewnames.default_view = func_or_cls
