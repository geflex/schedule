import logging

from bottex2 import sqlalchemy as sqldb
from bottex2.bottex import Bottex
from bottex2.ext import users
from bottex2.platforms.tg import TgReceiver
from bottex2.platforms.vk import VkReceiver
from schedule import start_logic, models, configs, env


def get_bottex():
    middlewares = [
        env.i18n.Middleware,
        users.user_middleware(models.User),
    ]
    receivers = [
        TgReceiver(None, token=configs.tg.token),
        VkReceiver(None, token=configs.vk.token, group_id=configs.vk.group_id),
    ]
    return Bottex(start_logic.main, middlewares, receivers)


def setup_db():
    engine = sqldb.create_engine(configs.db_url)
    engine.create_tables()
    sqldb.set_engine(engine)


def main():
    setup_db()
    bottex = get_bottex()
    bottex.serve_forever()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
