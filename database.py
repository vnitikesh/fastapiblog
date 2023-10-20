from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

SQLALCHEMY_DATABASE_URL = 'sqlite:///./blog.db'
# SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:root@localhost:5432/sdi"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(bind = engine, autocommit= False, autoflush = False)

# Base = declarative_base()

# engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
# async_session_maker = sessionmaker(engine, class_ = AsyncSession, expire_on_commit= False)
Base: DeclarativeMeta = declarative_base()


