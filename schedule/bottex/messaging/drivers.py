import time
from abc import ABC, abstractmethod
from typing import Tuple, AsyncIterable, List

import bottex
from bottex.core import i18n
from bottex.views import viewnames
from bottex.models import UserModel, get_user_model
from bottex.messaging import Message, Keyboard


class AbstractDriver(ABC):
    site_name: str = None
    kb_class: Keyboard

    def __init__(self, name):
        self._name = name
        self.logger = bottex.logging.get_logger(repr(self))

    def __repr__(self):
        return f'{self.__class__.__name__}()'

    def create_kb(self, buttons):
        """
        creates buttons from the button list
        should return the buttons supported by this driver
        :type buttons: List[Button]
        """
        return self.kb_class.from_buttons(buttons)

    def get_user(self, uid):
        return get_user_model().get_user(self.site_name, uid)

    def get_view(self, name):
        return viewnames[name]

    async def run(self):
        async for request in self.listen():
            t = time.time()
            bottex.logger.debug(f'New message {text!r} from {uid!r}')
            parser_func = self.get_view(user.current_view)
            response = parser_func(request)
            bottex.logger.debug(f'Message time {time.time() - t}')
            await self.send(response, user)

    # abstract methods

    @abstractmethod
    async def listen(self):
        """
        :yields: request
        :rtype: AsyncIterable[Request]
        """
        yield

    @abstractmethod
    async def send(self, response, user):
        """
        Sends the response to the user
        :param response: text message, picture or other type supported by driver
        :type response: Message

        :param user: user object with data about user
        :type user: UserModel
        """
        pass


class Request:
    """
    :type user: UserModel
    :type msg: str
    :type locale: str | None
    :type parsed:
    """
    def __init__(self, user, msg, locale=None):
        self.user = user
        self.msg = msg
        self.locale = locale
        self.parsed = None

        self.real_locale = user.locale or locale
        self.gettext = i18n.get_locale(self.real_locale.name)

    def __repr__(self):
        return f'Message(user={self.user}, msg={self.msg}, locale={self.locale})'