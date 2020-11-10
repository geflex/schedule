from abc import ABC, abstractmethod
from typing import Optional, List


class Button:
    def __init__(self, label: str, color: Optional[str] = None):
        self.label = label
        self.color = color


Buttons = List[List[Button]]


class Keyboard(ABC):
    def __init__(self, buttons: Buttons = None, one_time=False, inline=False):
        self.one_time = one_time
        self.inline = inline
        self.buttons = buttons or []

    def add_line(self, *buttons: Button):
        self.buttons.append(list(buttons))

    def add_button(self, button: Button):
        if not self.buttons:
            self.buttons.append([])
        self.buttons[-1].append(button)

    def insert_line(self, *buttons: Button):
        self.buttons.insert(0, list(buttons))

    def insert_button(self, button: Button):
        if not self.buttons:
            self.buttons.append([])
        self.buttons[0].append(button)

    def empty(self):
        return not bool(self.buttons)

    def __iter__(self):
        yield from self.buttons


class AbstractChat(ABC):
    @abstractmethod
    async def send_message(self, text: Optional[str] = None, kb: Optional[Keyboard] = None):
        pass


class ChatMiddleware(AbstractChat):
    def __init__(self, chat: AbstractChat):
        self.chat = chat

    async def send_message(self, text: Optional[str] = None, kb: Optional[Keyboard] = None):
        await self.chat.send_message(text=text, kb=kb)
