import logging

from sqlalchemy import create_engine

from bottex2.platforms.tg import TgReceiver
from bottex2.platforms.vk import VkReceiver

from bottex2.middlewares import loggers, users
from bottex2 import sqlalchemy as sqldb
from bottex2.bottex import Bottex

from schedule import logic, models, configs


def get_bottex():
    bottex = Bottex(
        TgReceiver(configs.tg.token),
        VkReceiver(configs.vk.token, configs.vk.group_id),
    )
    bottex.set_handler(logic.main)
    return bottex


def setup_db():
    # db = create_engine('sqlite://')
    db = create_engine('postgres://bysqdjznormjbf:c41a168449bf9c5721cc3c68d01b0b9b5dc903d9fe292457300f9bda0028bebb@ec2-54-75-229-28.eu-west-1.compute.amazonaws.com:5432/debevur5ab08ov')
    sqldb.create_tables(db)
    sqldb.set_engine(db)
    users.set_user_model(models.User)


def set_middlewares(bottex):
    bottex.add_middleware(users.UserBottexHandlerMiddleware)
    bottex.add_middleware(loggers.BottexLoggingHandlerMiddleware)
    bottex.add_middleware(loggers.BottexLoggingChatMiddleware)


def main():
    setup_db()
    bottex = get_bottex()
    set_middlewares(bottex)
    bottex.serve_forever()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
