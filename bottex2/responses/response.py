from __future__ import annotations
import warnings
from abc import ABC
from typing import Optional, List

from bottex2.messages import Media
from bottex2.chat import Keyboard, Buttons


class Request:
    def response(self) -> Response:
        pass

    def keyboard(self) -> Keyboard:
        pass

    def message(self) -> Message:
        pass


class Response(ABC):
    def __init__(self):
        self.keyboard = None  # type: Optional[Keyboard]
        self._messages = []  # type: List[Message]

    def add_message(self,
                    text: Optional[str] = None,
                    media: Optional[Media] = None,
                    kb: Optional[Keyboard] = None):
        self._messages.append(Message(text, media))

    def set_buttons(self, buttons: Buttons):
        self.keyboard = Keyboard(buttons)


class Message:
    def __init__(self, text: Optional[str] = None, media: Optional[List[Media]] = None):
        self.text = text
        self._media = media

    def set_text(self, text: str):
        warnings.warn('Message.set_text is deprecated', category=DeprecationWarning)
        self.text = text

    def add_media(self, media: Media):
        self._media.append(media)
