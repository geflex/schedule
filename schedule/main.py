import logging

import motor.motor_asyncio as motor_asyncio
from sqlalchemy import create_engine

from bottex2.platforms.tg import TgReceiver
from bottex2.platforms.vk import VkReceiver

from bottex2.middlewares import loggers, users
from bottex2.databases.mongodb import MongoUser
from bottex2.databases import sqlalchemy as sql
from bottex2.bottex import Bottex

from schedule import logic


bottex = Bottex(
    TgReceiver('schedule/auth_data/tg.json'),
    VkReceiver('schedule/auth_data/vk.json'),
)
bottex.set_handler(logic.main)


def set_mongo_user_model():
    users.set_user_model(MongoUser)
    mongo = motor_asyncio.AsyncIOMotorClient('localhost', 27017)
    MongoUser.set_collection(mongo.schedule_test.users)


def set_sql_user_model():
    addr = 'geflex.mysql.pythonanywhere-services.com'
    engine = create_engine('sqlite:///./schedule/foo.db')  # pool_recycle=280)
    sql.create_tables(engine)
    sql.set_engine(engine)
    users.set_user_model(sql.SqlAalchemyUser)


def set_middlewares():
    bottex.add_middleware(users.UserBottexHandlerMiddleware)
    bottex.add_middleware(loggers.BottexLoggingHandlerMiddleware)
    bottex.add_middleware(loggers.BottexLoggingChatMiddleware)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    set_sql_user_model()
    set_middlewares()
    bottex.serve_forever()
