import sys; sys.path.extend(['D:\\Documents\\Code\\Python\\schedule'])
import logging

import motor.motor_asyncio
from sqlalchemy import create_engine

from bottex2.platforms.tg import TgReceiver
from bottex2.platforms.vk import VkReceiver

from bottex2.middlewares import loggers, users
from bottex2.databases.mongodb import MongoUser
from bottex2.databases.sqlalchemy import SqlAalchemyUser, set_engine, Base
from bottex2.bottex import Bottex

from schedule import logic


bottex = Bottex(
    TgReceiver('auth_data/tg.json'),
    VkReceiver('auth_data/vk.json'),
)
bottex.set_handler(logic.main)


def set_mongo_user_model():
    users.set_user_model(MongoUser)
    mongo = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)
    MongoUser.set_collection(mongo.schedule_test.users)


def set_sql_user_model():
    addr = 'geflex.mysql.pythonanywhere-services.com'
    engine = create_engine('sqlite:///./foo.db')  # pool_recycle=280)
    set_engine(engine)
    users.set_user_model(SqlAalchemyUser)
    Base.metadata.create_all(engine)


def set_middlewares():
    bottex.add_middleware(users.UserBottexHandlerMiddleware)
    bottex.add_middleware(loggers.BottexLoggingHandlerMiddleware)
    bottex.add_middleware(loggers.BottexLoggingChatMiddleware)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    set_sql_user_model()
    set_middlewares()
    bottex.serve_forever()
