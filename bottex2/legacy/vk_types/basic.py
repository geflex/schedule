from datetime import datetime as dt

from bottex2.dict_parser import DictParser, Attr, Array
from bottex2.legacy.vk_types.media import parse_media


class Geo(DictParser):
    type = Attr()
    coordinates = Attr()
    place = Attr()


class Message(DictParser):
    """
    api version >= 5.80
    https://vk.com/dev/objects/message
    """
    id: int = Attr()
    date: dt.utcfromtimestamp = Attr()
    peer_id = Attr()
    from_id = Attr()
    text = Attr()
    random_id = Attr()
    attachments: Array(parse_media) = Attr()
    important = Attr()
    geo: Geo = Attr()
    payload = Attr()
    fwd_messages: 'Message' = Attr(is_optional=True)
    action = Attr()
