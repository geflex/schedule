import logging

from bottex2.bottex import Bottex
from bottex2.ext import users
from bottex2.platforms.tg import TgServer
from bottex2.platforms.vk import VkServer
from schedule import start_logic, models, configs


def get_bottex():
    middlewares = [
        models.i18n.Middleware,
        users.user_middleware(models.User),
    ]
    servers = [
        TgServer(None, token=configs.tg.token),
        VkServer(None, token=configs.vk.token, group_id=configs.vk.group_id),
    ]
    return Bottex(start_logic.main, middlewares, servers)


def main():
    bottex = get_bottex()
    bottex.serve_forever()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
