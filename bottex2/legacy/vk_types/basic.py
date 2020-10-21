from datetime import datetime as dt

from bottex2.legacy.dict_schema import DictSchema, Attr, Array
from bottex2.legacy.vk.objects import parse_media


class Geo(DictSchema):
    type = Attr()
    coordinates = Attr()
    place = Attr()


class Message(DictSchema):
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
