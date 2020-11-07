from sqlalchemy import Column, types as sqltypes

from models import Rights


class RightsMixin:
    rights = Column(sqltypes.Enum(Rights))
