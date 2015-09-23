from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Unicode


Base = declarative_base()


class Music(Base):

    id = Column(Integer, primary_key=True)

    name = Column(Unicode, nullable=False)

    __tablename__ = 'music'


class Tag(Base):

    id = Column(Integer, primary_key=True)

    name = Column(Unicode, nullable=False)

    t = Column(Unicode, nullable=False)

    __tablename__ = 'tag'
