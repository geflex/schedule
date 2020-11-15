import logging

from bottex2 import sqlalchemy as sqldb
from bottex2.bottex import Bottex
from bottex2.ext import users
from bottex2.platforms.tg import TgReceiver
from bottex2.platforms.vk import VkReceiver
from schedule import start_logic, models, configs, env


def get_bottex():
    bottex = Bottex(
        TgReceiver(configs.tg.token),
        VkReceiver(configs.vk.token, configs.vk.group_id),
        # VkCallbackReceiver(token=configs.vk.token,
        #                    group_id=configs.vk.group_id,
        #                    host=configs.host,
        #                    port=configs.vk.port,
        #                    path='',
        #                    secret=configs.vk.secret)
    )
    bottex.set_handler(start_logic.main)
    return bottex


def setup_db():
    engine = sqldb.create_engine(configs.db_url)
    engine.create_tables()
    sqldb.set_engine(engine)


def set_middlewares(bottex):
    bottex.add_middleware(env.i18n.Middleware)
    bottex.add_middleware(users.user_middleware(models.User))


def main():
    setup_db()
    bottex = get_bottex()
    set_middlewares(bottex)
    bottex.serve_forever()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
