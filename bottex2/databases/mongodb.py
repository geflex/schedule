from typing import Optional

import motor.motor_asyncio

from bottex2.middlewares.users import AbstractUser


def set_db(db: motor.motor_asyncio.AsyncIOMotorDatabase):
    MongoUser._collection = db[MongoUser.__tablename__]


class MongoUser(AbstractUser):
    __tablename__: Optional[str] = None
    _collection: Optional[motor.motor_asyncio.AsyncIOMotorCollection] = None

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

    async def update(self, **kwargs):
        await self._collection.update_one(self._obj, {'$set': kwargs})
        self._obj.update(kwargs)

    @property
    def platform(self):
        return self._obj['platform']

    @property
    def uid(self):
        return self._obj['uid']

    @property
    def state(self):
        return self._obj['state']
