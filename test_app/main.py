import sys; sys.path.extend(['D:\\Documents\\Code\\Python\\schedule'])
import logging

from bottex2.platforms.tg import TgReceiver
from bottex2.platforms.vk import VkReceiver

from bottex2.ext import logging as logging_ext, users
from bottex2.bottex import Bottex

from test_app import logic
from schedule import configs


def get_bottex():
    receivers = [
        TgReceiver(None, token=configs.tg.token),
        VkReceiver(None, token=configs.vk.token, group_id=configs.vk.group_id),
    ]
    middlewares = [
        users.UserBottexMiddleware,
        logging_ext.BottexLoggingMiddleware
    ]
    bottex = Bottex(logic.router, middlewares, receivers)
    return bottex


def main():
    set_sql_user_model()
    bottex = get_bottex()
    bottex.serve_forever()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
