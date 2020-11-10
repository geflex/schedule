import logging

from sqlalchemy import create_engine

from bottex2 import sqlalchemy as sqldb
from bottex2.bottex import Bottex
from bottex2.ext import users, i18n, lazy_chat
from bottex2.platforms.tg import TgReceiver
from bottex2.platforms.vk import VkReceiver
from schedule import start_logic, models, configs


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
    db = create_engine(configs.db_url)
    sqldb.create_tables(db)
    sqldb.set_engine(db)
    users.set_user_model(models.User)


def set_middlewares(bottex):
    bottex.add_middleware(i18n.TranslateBottexMiddleware)
    bottex.add_middleware(users.UserBottexMiddleware)
    bottex.add_middleware(lazy_chat.ResponseMiddleware)


def main():
    setup_db()
    bottex = get_bottex()
    set_middlewares(bottex)
    bottex.serve_forever()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
