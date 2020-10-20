from abc import ABC, abstractmethod
from typing import Optional, List


class Button:
    def __init__(self, label: str, color: Optional[str] = None):
        self.label = label
        self.color = color


Buttons = List[List[Button]]


class Keyboard(ABC):
    def __init__(self, buttons: Buttons, one_time=False, inline=False):
        self.one_time = one_time
        self.inline = inline
        self._buttons = []
        for line in buttons:
            new_line = []
            for btn in line:
                new_line.append(btn)
            self._buttons.append(new_line)
        if not self._buttons:
            self._buttons.append([])

    def add_line(self, *buttons: Button):
        self._buttons.append(list(buttons))

    def add_button(self, button: Button):
        self._buttons[-1].append(button)

    def __iter__(self):
        yield from self._buttons


class Chat(ABC):
    @abstractmethod
    async def send_message(self,
                           text: Optional[str] = None,
                           kb: Optional[Keyboard] = None):
        pass


class ChatMiddleware(Chat):
    def __init__(self, chat: Chat):
        self.chat = chat

    async def send_message(self, text: Optional[str] = None, kb: Optional[Keyboard] = None):
        await self.chat.send_message(text=text, kb=kb)
