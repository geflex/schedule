import warnings

from bottex.utils.dict_schema import DictSchema, Attr
from bottex.utils.enums import StrEnum, auto

from .basic import Message


class ClientInfo(DictSchema):
    button_actions = Attr()
    keyboard = Attr()
    inline_keyboard = Attr()
    lang_id = Attr()


class MessageEvent(DictSchema):
    message: Message = Attr()
    client_info: ClientInfo = Attr()


class VkEvents(StrEnum):
    """
    https://vk.com/dev/groups_events
    """
    message_new = auto()
    message_reply = auto()
    message_allow = auto()
    messages_deny = auto()

    photo_new = auto()
    photo_comment_new = auto()
    photo_comment_edit = auto()
    photo_comment_restore = auto()
    photo_comment_delete = auto()

    audio_new = auto()

    video_new = auto()
    video_comment_new = auto()
    video_comment_edit = auto()
    video_comment_restore = auto()
    video_comment_delete = auto()

    wall_post_new = auto()
    wall_repost = auto()

    wall_reply_new = auto()
    wall_reply_edit = auto()
    wall_reply_restore = auto()
    wall_reply_delete = auto()

    board_post_new = auto()
    board_post_edit = auto()
    board_post_restore = auto()
    board_post_delete = auto()

    market_comment_new = auto()
    market_comment_edit = auto()
    market_comment_restore = auto()
    market_comment_delete = auto()

    group_leave = auto()
    group_join = auto()
    user_block = auto()
    user_unblock = auto()

    poll_vote_new = auto()
    group_oficcers_edit = auto()
    group_change_settings = auto()
    group_change_photo = auto()


event_parsers = {
    VkEvents.message_new: MessageEvent,
}


def parse_event(request: dict):
    event_name, obj = request['type'], request['object']
    event = VkEvents[event_name]
    try:
        obj_parser = event_parsers[event]
    except KeyError:
        warnings.warn(f'Parser for event {event_name!r} does not exist')
        return event_name, obj
    return event, obj_parser(obj)
