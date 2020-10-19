import sys; sys.path.extend(['D:\\Documents\\Code\\Python\\schedule'])

import motor.motor_asyncio

from bottex2.platforms.tg import TgReceiver
from bottex2.platforms.vk import VkReceiver
from bottex2.platforms.sock import SockReciever

from bottex2.users import UserMiddleware, set_user_model
from bottex2.databases.mongodb import MongoUser
from bottex2.bottex import Bottex

from testing.test_app import logic


bottex = Bottex(
    TgReceiver('auth_data/tg.json'),
    VkReceiver('auth_data/vk.json'),
    SockReciever(port='8888'),
)
bottex.set_handler(logic.bug)


def setup_user_model():
    set_user_model(MongoUser)
    mongo = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)
    MongoUser.set_collection(mongo.schedule_test.users)
    bottex.add_middleware(UserMiddleware)


if __name__ == '__main__':
    setup_user_model()
    # logging.basicConfig(level=logging.INFO)
    bottex.serve_forever()
