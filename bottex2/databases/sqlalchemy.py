from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from bottex2.middlewares.users import AbstractUser


Base = declarative_base()
Session = sessionmaker()


def set_engine(engine):
    Session.configure(bind=engine)
    SqlAlchemyUser.session = Session()


def create_tables(engine):
    Base.metadata.create_all(engine)


class _UserModel(Base):
    __tablename__ = 'users'

    uid = Column(Integer, primary_key=True)
    platform = Column(String)
    state = Column(String)


class SqlAlchemyUser(AbstractUser):
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
            cls.session.add(user)
            cls.session.commit()
        return cls(user)

    async def update(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self.user, field, value)
        self.session.commit()
