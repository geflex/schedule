import logging

import motor.motor_asyncio

from bottex2.platforms.tg import TgReceiver
from bottex2.users import UserMiddleware, set_user_class
from bottex2.databases.mongodb import MongoUser
from bottex2.bottex import Bottex

from tests.test_app.router import router


import sys
sys.path.extend(['D:\\Documents\\Code\\Python\\schedule',
                 'D:\\Documents\\Code\\Python\\schedule\\schedule'])

def setup_users():
    set_user_class(MongoUser)
    mongo = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)
    MongoUser.set_collection(mongo.schedule_test.users)

receiver = Bottex(TgReceiver('auth_data/tg.json'))
receiver.add_middleware(UserMiddleware)
receiver.set_handler(router)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    receiver.serve_forever()
