import logging

from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import create_engine

from bottex2.platforms.tg import TgReceiver
from bottex2.platforms.vk import VkReceiver
from bottex2.platforms.tg_webhook import TgWebHookReceiver

from bottex2.middlewares import loggers, users
from bottex2.databases.mongodb import MongoUser
from bottex2.databases import sqlalchemy as sql
from bottex2.bottex import Bottex

from schedule import logic
from test_app.main import tg_config, vk_config


def get_bottex():
    bottex = Bottex(
        TgReceiver(**tg_config),
        VkReceiver(**vk_config),
        TgWebHookReceiver(**tg_config,
                          host='localhost',
                          port=3001,
                          sslfile='ssl/tg/vkapi.crt')
    )
    bottex.set_handler(logic.main)
    return bottex


def set_mongo_user_model():
    mongo = AsyncIOMotorClient('127.0.0.1', 27017)
    MongoUser.set_db(mongo.schedule_test)
    users.set_user_model(MongoUser)


def set_sql_user_model():
    # addr = 'geflex.mysql.pythonanywhere-services.com'
    engine = create_engine('sqlite:///./schedule/schedule.db')  # pool_recycle=280)
    sql.create_tables(engine)
    sql.set_engine(engine)
    users.set_user_model(sql.SqlAalchemyUser)


def set_middlewares(bottex):
    bottex.add_middleware(users.UserBottexHandlerMiddleware)
    bottex.add_middleware(loggers.BottexLoggingHandlerMiddleware)
    bottex.add_middleware(loggers.BottexLoggingChatMiddleware)


def main():
    set_sql_user_model()
    bottex = get_bottex()
    set_middlewares(bottex)
    bottex.serve_forever()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
