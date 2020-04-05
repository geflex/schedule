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
    current_view: str
    notifications: NotificationsModel

    @classmethod
    def get_user(cls, site, uid):
        pass

    def __init_subclass__(cls, **kwargs):
        global user_model
        user_model = cls


user_model = UserModel


def get_user_model():
    return user_model
