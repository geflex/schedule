import sys; sys.path.extend(['D:\\Documents\\Code\\Python\\schedule'])
import logging
import json

from motor.motor_asyncio import AsyncIOMotorClient

from bottex2.platforms.tg import TgReceiver
from bottex2.platforms.vk import VkReceiver

from bottex2.middlewares import loggers, users
from bottex2.databases.mongodb import MongoUser
from bottex2.bottex import Bottex

from test_app import logic, configs


def get_bottex():
    bottex = Bottex(
        TgReceiver(configs.tg.token),
        VkReceiver(configs.vk.token, configs.vk.group_id),
    )
    bottex.set_handler(logic.router)
    return bottex


def set_mongo_user_model():
    mongo = AsyncIOMotorClient('localhost', 27017)
    MongoUser.set_db(mongo['schedule_test'])
    users.set_user_model(MongoUser)


def set_middlewares(bottex):
    bottex.add_middleware(users.UserBottexHandlerMiddleware)
    bottex.add_middleware(loggers.BottexLoggingHandlerMiddleware)
    bottex.add_middleware(loggers.BottexLoggingChatMiddleware)


def main():
    set_mongo_user_model()
    bottex = get_bottex()
    set_middlewares(bottex)
    bottex.serve_forever()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
