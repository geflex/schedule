from copy import copy


class Message:
    def __init__(self, messages=None, buttons=None):
        self.messages = messages or []
        self.buttons = buttons or []

    def __iter__(self):
        yield from self.messages

    def __len__(self):
        return len(self.messages)

    def __getitem__(self, i):
        return self.messages.__getitem__(i)

    def append(self, message):
        self.messages.append(message)

    def extend(self, messages):
        self.messages.extend(m for m in messages if m)

    def copy(self):
        return Message(copy(self.messages), self.buttons)

    def __bool__(self):
        return any(m for m in self.messages) or bool(self.buttons)

    def __lshift__(self, other):
        response = self.copy()
        response.merge(other)
        return response

    def merge(self, other):
        if other is None:
            return
        self.override_buttons(other.buttons)
        if other.messages:
            self.extend(other.messages)

    def override_buttons(self, buttons):
        if not self.buttons or self.buttons == NoButtons:
            self.buttons = buttons

    def with_buttons(self, buttons):
        copied = self.copy()
        copied.override_buttons(buttons)
        return copied


class Text(Message):
    def __init__(self, text, buttons=None, attachments=None, translated=True):
        super().__init__([], buttons)
        self.text = text if text else None
        self.attachments = [] if attachments is None else attachments
        self.translated = translated
        if self.text:
            self.messages.append(self)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.text!r})'

    def __bool__(self):
        return bool(self.text or self.buttons or self.attachments)


class Buttons(Message):
    def __init__(self, buttons):
        super().__init__([], buttons)


class Attachment(Text):
    def __init__(self):
        super().__init__(None, [self])


class NoButtons:
    pass
