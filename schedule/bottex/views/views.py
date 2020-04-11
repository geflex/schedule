from typing import List, Iterator
from abc import ABC, abstractmethod

from bottex.core.logging import logger
from bottex.drivers import Message, Text, Button, Handler, Request
from bottex.utils.manager import NameManager
from bottex.utils.lazy import Unloaded


class Link(ABC):
    def __init__(self,
                 handler: Handler,
                 response: Message = None,
                 next_handler: Handler = None):
        self._handler = handler
        self.response = response
        self.next_handler = next_handler

    @abstractmethod
    def match(self, request: Request) -> bool:
        pass

    def handler(self, request):
        response = self._handler(request)
        if self.response:
            response = self.response << response
        if self.next_handler:
            next_resp = self.next_handler(request)
            if next_resp:
                response = response << next_resp
        return response

    def __repr__(self):
        return '{}(handler={}, response={}, next_handler={})'.format(
            self.__class__.__name__,
            self.handler, self.response, self.next_handler,
        )


class AddLink:
    def __init__(self, link):
        self.link = link
        self.handler = None

    def __call__(self, handler):
        self.handler = handler
        return self

    def get_link(self):
        self.link._handler = self.handler
        return self.link


class View(ABC):
    __viewname__: str

    links: List[Link]

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

    hello = Text('')
    success = Text('')
    error = Text('Error')
    cannot_parse = Text('Unknown command')

    def error_handler(self, request, e) -> Message:
        return self.error

    def cannot_parse_handler(self, request) -> Message:
        return self.cannot_parse

    def __init_subclass__(cls, isbase=False, **kwargs):
        if not isbase:
            if '.' in cls.__viewname__:
                raise ValueError('__viewname__ must not contain dots')
            if not isinstance(cls.__viewname__, str):
                raise TypeError('__viewname__ must be str')

            for name, val in cls.__dict__.items():
                if isinstance(val, AddLink):
                    cls.links.append(val.get_link())

            viewnames[cls.__viewname__] = cls.handle
            viewclasses[cls.__name__] = cls

    def __init__(self, request):
        self.request = request

    @classmethod
    def handle(cls, request) -> Message:
        return cls(request)._get_response()

    @classmethod
    def switch(cls, request) -> Message:
        self = cls(request)
        self._save_state()
        response = self.hello
        return response.with_buttons(self.buttons)

    def _get_response(self) -> Message:
        """
        Parse the text message passed in request and return the response
        """
        handler = self._get_handler()
        try:
            response = handler(self.request)
        except Exception as e:
            logger.error(e, exc_info=True)
            response = self.error_handler(self.request, e)
        return response.with_buttons(self.buttons)

    def _get_handler(self) -> Handler:
        """
        Returns the handler of link that matches current request.
        If the link does not exist, returns `self.cannot_parse_handler`
        """
        for link in self.links:
            if isinstance(link, Link) and link.match(self.request):
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
viewclasses = ViewManager()
