import logging

from bottex2.bottex import Bottex
from bottex2.ext import users
from bottex2.platforms.tg import TgReceiver
from bottex2.platforms.vk import VkReceiver
from schedule import start_logic, models, configs


def get_bottex():
    middlewares = [
        models.i18n.Middleware,
        users.user_middleware(models.User),
    ]
    receivers = [
        TgReceiver(None, token=configs.tg.token),
        VkReceiver(None, token=configs.vk.token, group_id=configs.vk.group_id),
    ]
    return Bottex(start_logic.main, middlewares, receivers)


def main():
    bottex = get_bottex()
    bottex.serve_forever()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
