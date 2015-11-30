import os

from pytest import fixture, yield_fixture
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session

from .entities import Base, Music, Tag

TEST_DATABASE_URL = os.environ.get('DODOTABLE_TEST_DATABASE_URL',
                                   'sqlite:///dodotable_test.db')


@yield_fixture
def fx_session():
    engine = create_engine(TEST_DATABASE_URL)
    try:
        metadata = Base.metadata
        metadata.drop_all(bind=engine)
        metadata.create_all(bind=engine)
        session = Session(bind=engine)
        yield session
        session.rollback()
        metadata.drop_all(bind=engine)
    finally:
        engine.dispose()


@fixture
def fx_music(fx_session):
    music = Music(name=u'9 crimes')
    fx_session.add(music)
    fx_session.commit()
    return music


@fixture
def fx_tags(fx_session):
    genre = Tag(t='genre', name='Acoustic')
    country = Tag(t='country', name='irish')
    fx_session.add(genre)
    fx_session.add(country)
    fx_session.commit()
    return genre, country
