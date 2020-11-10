import sys; sys.path.extend(['D:\\Documents\\Code\\Python\\schedule'])
import logging

from bottex2.platforms.tg import TgReceiver
from bottex2.platforms.vk import VkReceiver

from bottex2.ext import logging as logging_ext, users
from bottex2.bottex import Bottex

from test_app import logic
from schedule import configs


def get_bottex():
    bottex = Bottex(
        TgReceiver(configs.tg.token),
        VkReceiver(configs.vk.token, configs.vk.group_id),
    )
    bottex.set_handler(logic.router)
    return bottex


def set_middlewares(bottex):
    bottex.add_middleware(users.UserBottexMiddleware)
    bottex.add_middleware(logging_ext.BottexLoggingMiddleware)
    bottex.add_middleware(logging_ext.BottexLoggingChatMiddleware)


def main():
    set_sql_user_model()
    bottex = get_bottex()
    set_middlewares(bottex)
    bottex.serve_forever()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
