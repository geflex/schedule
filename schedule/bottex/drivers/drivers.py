import time
from abc import ABC, abstractmethod
from typing import Callable, Optional, Iterable, AsyncIterator

import bottex
from bottex.drivers import Message, Text
from bottex.models import users, UserModel
from bottex.utils import i18n


Handler = Callable[[Message], Optional[Message]]
ErrorHandler = Callable[[Message, Exception], Message]


class Request(dict):
    """
    :type user: UserModel
    :type msg: Text
    :type parsed:
    """
    def __init__(self, user, msg):
        super().__init__()
        self.user = user
        self.msg = msg
        self.parsed = None

        self.real_locale = user.locale or self.get('locale')
        self.gettext = i18n.get_locale(self.real_locale.name)

    def __repr__(self):
        return f'Message(user={self.user}, msg={self.msg})'


class Driver(ABC):
    site_name: str = None

    def get_user(self, uid):
        """get user by id"""
        return users.user_model.get_or_add(self.site_name, uid)

    async def run(self):
        async for request in self.listen():
            t = time.time_ns()
            bottex.logger.debug(f'New message {request.msg.text!r} from {request.user.uid!r}')

            handler = self.get_handler(request.user.last_view)
            response = handler(request)

            bottex.logger.debug(f'Handle time {(time.time_ns() - t)/1E6} ms')
            await self.send(response, request.user)

    # abstract methods

    @abstractmethod
    def get_handler(self, name):
        """
        get handler by name
        :param name:
        :return: Handler
        """

    @abstractmethod
    def create_kb(self, buttons):
        """
        creates buttons from the button list
        should return the buttons supported by this driver
        :type buttons: Iterable[Button]
        """

    @abstractmethod
    async def listen(self):
        """
        :yields: request
        :rtype: AsyncIterator[Request]
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
