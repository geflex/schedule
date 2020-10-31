from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Session = sessionmaker()


# noinspection PyArgumentList
class _Base:
    session = Session()

    @classmethod
    async def get(cls, **kwargs):
        user = cls.session.query(cls).filter_by(**kwargs).one_or_none()
        if user is None:
            user = cls(**kwargs)
            cls.session.add(user)
            cls.session.commit()
        return user

    async def update(self, **kwargs):
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)
            else:
                raise AttributeError(f'There is no column {field} in {self.__tablename__}')
        self.session.commit()


Base = declarative_base(cls=_Base)


def set_engine(engine):
    Base.session.bind = engine


def create_tables(engine):
    Base.metadata.create_all(engine)
