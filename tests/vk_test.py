from drivers.vk_objects.events import parse_event
from drivers.vk_objects.media import parse_media

id_ = 470196435
date = 1552021035

audio = {

}

video = {

}

req = {'type': 'message_new',
       'object': {
           'id': id_,
           'date': date,
           'attachments': [
               {'type': 'audio', 'audio': audio},
               {'type': 'video', 'video': video},
           ]
       }}


def main():
    typ, obj = parse_event(req)
    print(obj.date)


if __name__ == '__main__':
    main()
