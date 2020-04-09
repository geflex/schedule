from .messages import Attachment


class Picture(Attachment):
    def __init__(self, path=None):
        super().__init__()
        self.path = path


class Video(Attachment):
    def __init__(self, path=None):
        super().__init__()
        self.path = path


class Audio(Attachment):
    def __init__(self, path=None):
        super().__init__()
        self.path = path


class Doc(Attachment):
    def __init__(self, path=None):
        super().__init__()
        self.path = path


class Wall(Attachment):
    pass


class Market(Attachment):
    pass


class Location(Attachment):
    pass
