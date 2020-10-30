import logging

from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import create_engine

from bottex2.platforms.tg import TgReceiver
from bottex2.platforms.vk import VkReceiver

from bottex2.middlewares import loggers, users
from bottex2.databases import mongodb
from bottex2.databases import sqlalchemy as sqldb
from bottex2.bottex import Bottex

from . import logic
from test_app import configs


def get_bottex():
    bottex = Bottex(
        TgReceiver(configs.tg.token),
        VkReceiver(configs.vk.token, configs.vk.group_id),
    )
    bottex.set_handler(logic.main)
    return bottex


def set_mongo_user_model():
    conn = AsyncIOMotorClient('mongodb://localhost:27017')
    mongodb.set_db(conn.schedule_test)
    users.set_user_model(mongodb.MongoUser)


def set_sql_user_model():
    db = create_engine('sqlite:///./schedule/schedule.db')
    sqldb.create_tables(db)
    sqldb.set_engine(db)
    users.set_user_model(sqldb.SqlAlchemyUser)


def set_memory_user_model():
    users.set_user_model(users.TempUser)


def set_middlewares(bottex):
    bottex.add_middleware(users.UserBottexHandlerMiddleware)
    bottex.add_middleware(loggers.BottexLoggingHandlerMiddleware)
    bottex.add_middleware(loggers.BottexLoggingChatMiddleware)


def main():
    set_memory_user_model()
    bottex = get_bottex()
    set_middlewares(bottex)
    bottex.serve_forever()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
