import asyncio
import sys; sys.path.extend(['D:\\Documents\\Code\\Python\\schedule'])
import logging

import motor.motor_asyncio

from bottex2.platforms.tg import TgReceiver
from bottex2.platforms.vk import VkReceiver
from bottex2.platforms.sock import SockReciever
from bottex2.platforms.py import PyReceiver

from bottex2.users import UserMiddleware, set_user_model
from bottex2.databases.mongodb import MongoUser
from bottex2.bottex import Bottex

# noinspection PyUnresolvedReferences,PyPackageRequirements
from router import router
# noinspection PyUnresolvedReferences,PyPackageRequirements
from bench import bench


py_reseiver = PyReceiver()
receiver = Bottex(
    TgReceiver('auth_data/tg.json'),
    VkReceiver('auth_data/vk.json'),
    SockReciever(port='8888'),
    py_reseiver,
)
receiver.set_handler(router)


def setup_user_model():
    set_user_model(MongoUser)
    mongo = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)
    MongoUser.set_collection(mongo.schedule_test.users)


async def main():
    receiver.add_middleware(UserMiddleware)
    await asyncio.gather(
        bench(py_reseiver, 1E5),
        receiver.serve_async(),
    )


if __name__ == '__main__':
    setup_user_model()
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
