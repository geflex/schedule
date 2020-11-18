from functools import partial

from sqlalchemy.ext.declarative import declarative_base as _declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import MetaData

Session = sessionmaker()


# noinspection PyArgumentList
class _Model:
    session = Session()
    metadata: MetaData
    __tablename__: str

    @classmethod
    def set_engine(cls, engine):
        cls.session.bind = engine

    @classmethod
    def create_tables(cls):
        cls.metadata.create_all(cls.session.bind)

    @classmethod
    async def get_or_create(cls, **kwargs):
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

    async def delete(self):
        self.session.delete(self)
        self.session.commit()


declarative_base = partial(_declarative_base, cls=_Model)
Model = declarative_base()
