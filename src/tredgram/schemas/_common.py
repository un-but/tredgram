"""Основная схема с общими для всех схем настройками."""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, model_validator
from sqlalchemy.orm import DeclarativeBase


class BaseSchema(BaseModel):
    """Базовый класс для схем."""

    model_config: ClassVar[ConfigDict] = {
        "from_attributes": True,
        "extra": "ignore",
        "arbitrary_types_allowed": True,
    }  # Позволяет создавать модели из атрибутов модели ORM и использовать сторонние схемы

    _deferred: ClassVar[tuple[str, ...]] = ()

    @model_validator(mode="before")
    def validate_deferred_values(cls, values: Any) -> Any:
        # Преобразование из ORM
        if isinstance(values, DeclarativeBase):
            return {
                key: value
                for key, value in values.__dict__.items()
                if key or key not in cls._deferred
            }

        return values


class SuccessResponse(BaseSchema):
    """Схема ответа при успешной обработке входящих событий."""

    ok: bool = True
