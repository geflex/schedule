from bottex2.legacy.dict_parser import DictParser, Attr

from .basic import Message


class ClientInfo(DictParser):
    button_actions = Attr()
    keyboard = Attr()
    inline_keyboard = Attr()
    lang_id = Attr()


class MessageEvent(DictParser):
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
        return event_name, obj
    return event_name, obj_parser(obj)
