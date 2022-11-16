from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from aioredis import from_url
from os import getenv


postgres_engine = create_async_engine(f'postgresql+asyncpg://{getenv("POSTGRES_USER")}:{getenv("POSTGRES_PASSWORD")}@{getenv("POSTGRES_URL")}:{getenv("POSTGRES_PORT")}/{getenv("POSTGRES_DB")}')
redis = from_url(f'redis://{getenv("REDIS_URL")}', password=getenv('REDIS_PASSWORD'))
session = sessionmaker(postgres_engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_session():
    async with session() as ses:
        yield ses
