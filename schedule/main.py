import logging

from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import create_engine

from bottex2.platforms.tg_webhook import TgWebHookReceiver

from bottex2.middlewares import loggers, users
from bottex2.databases.mongodb import MongoUser
from bottex2.databases import sqlalchemy as sql
from bottex2.bottex import Bottex

from schedule import logic
from test_app.main import tg_data


bottex = Bottex(
    TgWebHookReceiver(tg_data['token'],
                      host='localhost',
                      port=3001,
                      path='/tg',
                      sslfile='ssl/tg/vkapi.crt')
)
bottex.set_handler(logic.main)


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


def set_middlewares():
    bottex.add_middleware(users.UserBottexHandlerMiddleware)
    bottex.add_middleware(loggers.BottexLoggingHandlerMiddleware)
    bottex.add_middleware(loggers.BottexLoggingChatMiddleware)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    set_sql_user_model()
    set_middlewares()
    bottex.serve_forever()
