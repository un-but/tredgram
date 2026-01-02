"""Модуль, отвечающий за подключение к базе данных."""

from __future__ import annotations

from collections.abc import AsyncIterator

import redis.asyncio as async_redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from tredgram.schemas import config

engine = create_async_engine(
    url=config.database.ps_url.get_secret_value(),
    echo=config.database.echo,
    pool_size=20,  # основной пул
    max_overflow=20,  # дополнительные соединения
    pool_timeout=60,  # таймаут ожидания (сек)
)

# Позволяет создавать сессии с правильными настройками
session_maker = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)

rd = async_redis.from_url(config.database.ps_url.get_secret_value(), decode_responses=True)


async def get_db() -> AsyncIterator[AsyncSession]:
    """Создает подключение к базе данных для инъекции зависимостей FastAPI.

    Returns:
        AsyncIterator[AsyncSession]: генератор асинхронной сессии.

    Yields:
        Iterator[AsyncIterator[AsyncSession]]: _description_

    """
    async with session_maker() as db:
        yield db


def get_redis() -> async_redis.Redis:
    return rd
