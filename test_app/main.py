import sys; sys.path.extend(['D:\\Documents\\Code\\Python\\schedule'])
import logging
import json

from motor.motor_asyncio import AsyncIOMotorClient

from bottex2.platforms.tg import TgReceiver
from bottex2.platforms.vk import VkReceiver

from bottex2.middlewares import loggers, users
from bottex2.databases.mongodb import MongoUser
from bottex2.bottex import Bottex

from test_app import logic


tg_data = json.load(open('schedule/auth_data/tg.json'))
vk_data = json.load(open('schedule/auth_data/vk.json'))


bottex = Bottex(
    TgReceiver(tg_data['token']),
    VkReceiver(vk_data['token'], vk_data['group_id']),
)
bottex.set_handler(logic.router)


def setup_user_model():
    mongo = AsyncIOMotorClient('localhost', 27017)
    MongoUser.set_db(mongo['schedule_test'])
    users.set_user_model(MongoUser)


def set_middlewares():
    bottex.add_middleware(users.UserBottexHandlerMiddleware)
    bottex.add_middleware(loggers.BottexLoggingHandlerMiddleware)
    bottex.add_middleware(loggers.BottexLoggingChatMiddleware)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    setup_user_model()
    set_middlewares()
    bottex.serve_forever()
