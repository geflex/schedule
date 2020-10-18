from typing import Optional

import motor.motor_asyncio

from bottex2.users import AbstractUser


class MongoUser(AbstractUser):
    _collection: Optional[motor.motor_asyncio.AsyncIOMotorCollection] = None

    @classmethod
    def set_collection(cls, collection: motor.motor_asyncio.AsyncIOMotorCollection):
        cls._collection = collection

    @classmethod
    async def get(cls, platform, uid):
        init_data = {
            'uid': uid,
            'platform': platform,
        }
        obj = await cls._collection.find_one(init_data)
        if obj is None:
            init_data.update(state=None)
            await cls._collection.insert_one(init_data)
            obj = init_data
        return cls(obj)

    def __init__(self, obj):
        self._obj = obj

    async def update(self, state=None):
        update = {'state': state}
        await self._collection.update_one(self._obj, {'$set': update})
        self._obj.update(update)

    @property
    def platform(self):
        return self._obj['platform']

    @property
    def uid(self):
        return self._obj['uid']

    @property
    def state(self):
        return self._obj['state']
