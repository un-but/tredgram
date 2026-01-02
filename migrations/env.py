"""Файл настройки автогенерации обновлений базы данных на основе изменений."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from tredgram.db.models import BaseModel
from tredgram.schemas import config

url = config.database.ps_url.get_secret_value()  # Секретный url из .env

# Настраивает логгер
fileConfig("logconfig.ini")

# Объект метаданных базовой модели для поддержки автогенерации миграций
target_metadata = BaseModel.metadata


def run_migrations_offline() -> None:
    """Запускает миграции в "офлайн" режиме.

    Это позволяет вывести готовую sql инструкцию, используя только URL.
    При этом Engine или DBAPI не требуются.

    Вызов context.execute() здесь возвращает строку вместо выполнения действий.
    """
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,  # Заменяет параметризированный запрос на обычный
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запускает миграции в "онлайн" режиме.

    При выполнении миграции сразу будут применены к базе данных.
    """
    asyncio.run(run_async_migrations())


async def run_async_migrations() -> None:
    """Создает AsyncEngine с учетом контекста и асинхронно выполняет миграции."""
    connectable = async_engine_from_config(
        {
            **context.config.get_section(context.config.config_ini_section, {}),
            "sqlalchemy.url": url,
        },
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def do_run_migrations(connection: Connection) -> None:
    """Настраивает контекст Alembic и выполняет миграции одной транзакцией.

    Args:
        connection (Connection): SQLAlchemy соединение с базой данных.

    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
