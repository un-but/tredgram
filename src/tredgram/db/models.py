"""Модели SQLAlchemy ORM."""

from __future__ import annotations

import re
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)
from sqlalchemy.types import BigInteger

rename_pattern = re.compile(r"(?<!^)(?=[A-Z])")


class BaseModel(DeclarativeBase):
    """Базовый класс для моделей SQLAlchemy.

    Автоматически генерирует имя таблицы в snake_case во множественном числе.
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Генерирует имя таблицы из имени класса."""
        class_name = re.sub(
            rename_pattern,
            "_",
            cls.__name__.replace("Model", ""),
        ).lower()
        return class_name + "s" if class_name[-1] != "y" else class_name[:-1] + "ies"


# __replace__ далее идет пример работы моделей


class UserModel(BaseModel):
    """Модель пользователя."""

    tg_id: Mapped[BigInteger] = mapped_column(BigInteger, primary_key=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    username: Mapped[str]

    first_name: Mapped[str]
    last_name: Mapped[str]
    full_name: Mapped[str]

    language: Mapped[str] = mapped_column(String(3))
    is_active: Mapped[bool] = mapped_column(default=True)

    posts: Mapped[list[PostModel]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="raise",
    )


class PostModel(BaseModel):
    """Модель поста."""

    id: Mapped[BigInteger] = mapped_column(BigInteger, primary_key=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    content: Mapped[str] = mapped_column(String(1000))

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped[UserModel] = relationship(back_populates="posts", lazy="raise")
