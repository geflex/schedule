import warnings

from bottex.utils.enums import LowerEnum, auto
from bottex.utils.dict_schema import DictSchema, Attr


class Photo(DictSchema):
    """
    api version from 5.77
    https://vk.com/dev/objects/photo
    """
    id = Attr()
    album_id = Attr()
    owner_id = Attr()
    user_id = Attr()
    text = Attr()
    date = Attr()
    sizes = Attr()
    width = Attr()
    height = Attr()


class Audio(DictSchema):
    """
    api version from 5.0
    https://vk.com/dev/objects/audio
    """
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


class MediaTypes(LowerEnum):
    audio = auto()
    photo = auto()
    video = auto()
    document = auto()
    link = auto()
    market = auto()
    market_album = auto()
    wall = auto()
    wall_reply = auto()
    sticker = auto()
    gift = auto()


media_parsers = {
    MediaTypes.audio: Audio,
    MediaTypes.photo: Photo,
}


def parse_media(request: dict):
    media_name = request['type']
    media = request[media_name]
    media_type = MediaTypes[media_name]
    try:
        media_parser = media_parsers[media_type]
    except KeyError:
        warnings.warn(f'Parser for media type {media_name!r} does not exist')
        return media_type, media
    return media_type, media_parser(media)
