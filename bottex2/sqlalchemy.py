from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from bottex2.middlewares.users import UserModel

_Base = declarative_base()
Session = sessionmaker()


class Base(_Base):
    session: Session

    @classmethod
    async def get(cls, platform, uid):
        # noinspection PyArgumentList
        user = cls.session.query(cls).filter_by(uid=uid, platform=platform).one_or_none()
        if user is None:
            user = cls(uid=uid, platform=platform)
            cls.session.add(user)
            cls.session.commit()
        return cls(user)

    async def update(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self.user, field, value)
        self.session.commit()


def set_engine(engine):
    Session.configure(bind=engine)
    UserModel.session = Session()


def create_tables(engine):
    Base.metadata.create_all(engine)
