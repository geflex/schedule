from datetime import datetime

from bottex.utils.dict_schema import DictSchema, Attr, array
from drivers.vk_objects.media import parse_media


class Geo(DictSchema):
    type = Attr()
    coordinates = Attr()
    place = Attr()


class Message(DictSchema):
    """
    api version from 5.80
    https://vk.com/dev/objects/message
    """
    id: int = Attr()
    date: datetime.utcfromtimestamp = Attr()
    peer_id = Attr()
    from_id = Attr()
    text = Attr()
    random_id = Attr()
    attachments: array(parse_media) = Attr()
    important = Attr()
    geo: Geo = Attr()
    payload = Attr()
    fwd_messages: 'Message' = Attr(optional=True)
    action = Attr()
