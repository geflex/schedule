from abc import ABC, abstractmethod
from enum import Enum


class Color(Enum):
    BLUE = 'blue'
    GREEN = 'green'
    RED = 'red'
    WHITE = 'white'


class Button:
    def __init__(self, title, color=None, *, next_line=True, translate=True):
        """
        :type title: str
        :type color:
        """
        self.label = title
        self.color = color
        self.next_line = next_line
        self.translate = translate

    def __repr__(self):
        return f'{self.__class__.__name__}({self.label}, color={self.color}, next_line={self.next_line})'


class Keyboard(ABC):
    colors: dict

    @abstractmethod
    def add_button(self, button):
        pass

    @abstractmethod
    def get_str(self) -> str:
        pass

    @classmethod
    def from_buttons(cls, buttons) -> str:
        return ''
