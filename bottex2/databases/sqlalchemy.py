from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from bottex2.middlewares.users import AbstractUser


Base = declarative_base()
Session = sessionmaker()


def set_engine(engine):
    Session.configure(bind=engine)
    SqlAalchemyUser.session = Session()


class _UserModel(Base):
    __tablename__ = 'users'

    uid = Column(Integer, primary_key=True)
    platform = Column(String)
    state = Column(String)


class SqlAalchemyUser(AbstractUser):
    session: Session

    @property
    def state(self):
        return self.user.state

    @property
    def uid(self):
        return self.user.uid

    @property
    def platform(self):
        return self.user.platform

    def __init__(self, user: _UserModel):
        self.user = user

    @classmethod
    async def get(cls, platform, uid) -> 'AbstractUser':
        # noinspection PyArgumentList
        user = cls.session.query(_UserModel).filter_by(uid=uid, platform=platform).one_or_none()
        if user is None:
            user = _UserModel(uid=uid, platform=platform)
            user = cls.session.add(user)
            cls.session.commit()
        return user

    async def update(self, state=None):
        if state is not None:
            self.user.state = state
        self.session.add(self)
        self.session.commit()
