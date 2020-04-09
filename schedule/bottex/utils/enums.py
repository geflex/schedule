from enum import Enum, auto


class NoValueEnum(Enum):
    def __repr__(self):
        return f'<{self.__class__.__name__}.{self.name}>'


class StrEnum(NoValueEnum):
    # noinspection PyMethodParameters
    def _generate_next_value_(name, start, count, last_values):
        return name


class LowerEnum(StrEnum):
    # noinspection PyMethodParameters
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()


class UpperEnum(StrEnum):
    # noinspection PyMethodParameters
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()
