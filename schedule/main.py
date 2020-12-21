import logging

from bottex2.middlewares import WrappedHandler
from bottex2.multiplatform import MultiplatformTransport, MultiplatformWrappedHandler, manager
from bottex2.platforms.tg import TgTransport
from bottex2.platforms.vk import VkTransport
from bottex2.server import Server
from schedule import start_logic, configs
from schedule.models import users, i18n


def get_multiplatform_server():
    handler = MultiplatformWrappedHandler(start_logic.main, [
        i18n.Middleware,
        users.Middleware,
    ])
    transport = MultiplatformTransport([
        TgTransport(token=configs.tg.token),
        VkTransport(token=configs.vk.token, group_id=configs.vk.group_id),
    ])
    bottex = Server(transport, handler)
    return bottex


def get_vk_server():
    handler = WrappedHandler(start_logic.main, [
        i18n.Middleware,
        manager.get_child(users.Middleware, VkTransport),
    ])
    transport = VkTransport(configs.vk.token, configs.vk.group_id)
    return Server(transport, handler)


def main():
    server = get_multiplatform_server()
    server.serve_forever()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
