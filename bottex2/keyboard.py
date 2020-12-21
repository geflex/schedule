from typing import Optional, List


class Button:
    def __init__(self, label: str, color: Optional[str] = None):
        self.label = label
        self.color = color


Buttons = List[List[Button]]


class Keyboard(list, Buttons):
    def __init__(self, buttons: Buttons = None, one_time=False, inline=False):
        super().__init__(buttons or [])
        self.one_time = one_time
        self.inline = inline

    def append_line(self, *buttons: Button):
        self.append(list(buttons))

    def insert_line(self, *buttons: Button):
        self.insert(0, list(buttons))

    def append_button(self, button: Button):
        if not self:
            self.append([])
        self[-1].append(button)

    def insert_button(self, button: Button):
        if not self:
            self.append([])
        self[0].append(button)

    def empty(self):
        return not bool(self)
