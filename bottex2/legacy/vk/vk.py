vk_empty_text = '\u200b'


class VkKeyboard:
    colors = {
        Color.RED: VkColor.NEGATIVE,
        Color.WHITE: VkColor.DEFAULT,
        Color.BLUE: VkColor.PRIMARY,
        Color.GREEN: VkColor.POSITIVE,
        None: VkColor.DEFAULT,
    }

    def __init__(self):
        self.kb = VkApiKeyboard()

    def add_button(self, button):
        self.kb.add_button(button.label, self.colors[button.color])

    def add_line(self):
        self.kb.add_line()

    def pop_line(self):
        self.kb.lines.pop()

    def get_str(self):
        return self.kb.get_keyboard()

    @classmethod
    def from_buttons(cls, button_lines):
        if button_lines is None:
            return ''
        self = cls()
        for line in button_lines:
            for button in line:
                self.add_button(button)
            self.add_line()
        self.pop_line()
        return self.get_str()
