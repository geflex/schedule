import sys; sys.path.extend(['D:\\Documents\\Code\\Python\\schedule'])
import logging

import motor.motor_asyncio

from bottex2.platforms.tg import TgReceiver
from bottex2.platforms.vk import VkReceiver

from bottex2.middlewares import loggers, users
from bottex2.databases.mongodb import MongoUser
from bottex2.bottex import Bottex

from testing.test_app import logic


bottex = Bottex(
    TgReceiver('auth_data/tg.json'),
    VkReceiver('auth_data/vk.json'),
)
bottex.set_handler(logic.router)


def setup_user_model():
    users.set_user_model(MongoUser)
    mongo = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)
    MongoUser.set_collection(mongo.schedule_test.users)


def set_middlewares():
    bottex.add_handler_middleware(users.UserBottexHandlerMiddleware)
    bottex.add_handler_middleware(loggers.BottexLoggingHandlerMiddleware)
    bottex.add_chat_middleware(loggers.BottexLoggingChatMiddleware)


if __name__ == '__main__':
    setup_user_model()
    set_middlewares()
    logging.basicConfig(level=logging.INFO)
    bottex.serve_forever()
