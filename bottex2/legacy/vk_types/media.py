from enum import Enum

from bottex2.legacy.dict_parser import DictParser, Attr


class Photo(DictParser):
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


class Audio(DictParser):
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


class MediaTypes(Enum):
    audio = 'audio'
    photo = 'photo'
    video = 'video'
    document = 'document'
    link = 'link'
    market = 'market'
    market_album = 'market_album'
    wall = 'wall'
    wall_reply = 'wall_reply'
    sticker = 'sticker'
    gift = 'gift'


media_parsers = {
    MediaTypes.audio: Audio,
    MediaTypes.photo: Photo,
}


def parse_media(request: dict):
    media_name = request['type']
    media_type = request[media_name]
    try:
        media_parser = media_parsers[media_type]
    except KeyError:
        return media_type, media
    return media_type, media_parser(media)
