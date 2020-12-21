from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import MetaData

Session = sessionmaker()


class _QueryProperty:
    def __get__(self, instance, owner):
        return owner.session.query(owner)


# noinspection PyArgumentList
class BaseModel:
    session: Session
    metadata: MetaData
    query = _QueryProperty()
    __tablename__: str

    @classmethod
    def get_or_create(cls, **kwargs):
        instance = cls.query.filter_by(**kwargs).one_or_none()
        if instance is None:
            instance = cls(**kwargs)
            cls.session.add(instance)
        return instance

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


class SQLAlchemy:
    def __init__(self, engine: Engine, metadata=None, session=None):
        self.metadata = metadata
        self.session = session or Session()
        self.engine = engine
        self.Model = self.make_declarative_base()
        self.metadata = self.Model.metadata

    def make_declarative_base(self):
        Model = declarative_base(metadata=self.metadata, cls=BaseModel)
        Model.session = self.session
        Model.session.bind = self.engine
        return Model

    def create_all(self):
        self.metadata.create_all(self.session.bind)
