import datetime
from mongoengine import DynamicDocument


class NotificationsModel:
    allowed = False
    time: datetime.time = None


class UserModel:
    site: str
    uid: str
    locale: str
    rights: int
    last_view: str
    notifications: NotificationsModel

    @classmethod
    def get_or_add(cls, site, uid):
        pass

    def __init_subclass__(cls, **kwargs):
        global user_model
        user_model = cls


user_model = UserModel
