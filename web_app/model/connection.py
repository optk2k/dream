from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from model.config.database import async_url_db
from model.config.app import badlisted_words, spacy_nounphrases


class Base(DeclarativeBase):
    pass


DATABASE_URL = async_url_db


engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    """Get a database session."""
    async with async_session() as session:
        async with session.begin():
            yield session
