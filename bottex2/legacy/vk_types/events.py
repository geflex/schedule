import warnings

from bottex2.legacy.dict_schema import DictSchema, Attr

from .basic import Message


class ClientInfo(DictSchema):
    button_actions = Attr()
    keyboard = Attr()
    inline_keyboard = Attr()
    lang_id = Attr()


class MessageEvent(DictSchema):
    message: Message = Attr()
    client_info: ClientInfo = Attr()


# https://vk.com/dev/groups_events


event_parsers = {
    'message_new': MessageEvent,
}


def parse_event(request: dict):
    event_name, obj = request['type'], request['object']
    try:
        obj_parser = event_parsers[event_name]
    except KeyError:
        warnings.warn(f'Parser for event {event_name!r} does not exist')
        return event_name, obj
    return event_name, obj_parser(obj)
