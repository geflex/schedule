from enum import Enum, auto


class VkLanguages(Enum):
    ru = auto()
    uk = auto()
    be = auto()
    en = auto()
    sp = auto()
    fn = auto()
    de = auto()
    it = auto()


class DictParser:
    __version__ = None
    __attrs__ = []

    def __init__(self, obj: dict):
        self.raw = obj
        for attr in self.__attrs__:
            v = obj.pop(attr.name)
            setattr(self, attr.name, v)

    def __init_subclass__(cls, **kwargs):
        cls.__attrs__ = attrs = []
        for name, attr in cls.__dict__.items():
            if isinstance(attr, Attr):
                if not attr.name:
                    attr.name = name
                attrs.append(attr)


class Attr:
    def __init__(self, type=None):
        self.name = None
        self.type = type


class Photo(DictParser):
    __version__ = '>= 5.77'
    id = Attr()
    album_id = Attr()
    owner_id = Attr()
    user_id = Attr()
    text = Attr()
    date = Attr()
    sizes = Attr()
    width = Attr()
    height = Attr()


class Audio(DictParser):
    __version__ = '>= 5.0'
    id = Attr()
    owner_id = Attr()
    artist = Attr()
    title = Attr()
    duration = Attr()
    url = Attr()
    lyrics_id = Attr()
    album_id = Attr()
    genre_id = Attr()
    date = Attr()
    no_search = Attr()


class Message(DictParser):
    id = Attr()
    date = Attr()
    peer_id = Attr()
    from_id = Attr()
    text = Attr()
    random_id = Attr()
    attachments = Attr()
    important = Attr()
    geo = Attr()
    payload = Attr()
    fwd_messages = Attr()
    action = Attr()


obj_classes = {
    'message_new': Message,
}


def parse_event(request: dict):
    event_name, obj = request['type'], request['object']
    obj_cls = obj_classes[event_name]
    return event_name, obj_cls(obj)


class Event(DictParser):
    type = Attr()
    object = Attr()
