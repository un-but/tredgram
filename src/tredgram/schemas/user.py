"""Схемы для работы с пользователями."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import Field
from tredgram.schemas._common import BaseSchema

if TYPE_CHECKING:  # Требуется для корректной работы отложенного импорта
    from tredgram.schemas import PostChildResponse


class UserBase(BaseSchema):
    """Базовая схема пользователя."""

    id: int
    username: str

    first_name: str
    last_name: str
    full_name: str

    language: str = Field(max_length=3)


class UserCreate(UserBase):
    """Схема для создания пользователя."""


class UserResponse(UserBase):
    """Схема для ответа с данными пользователя."""

    created_at: datetime

    is_active: bool
    posts: list[PostChildResponse] | None = None

    _deferred = ("posts",)


class UserUpdate(BaseSchema):
    """Схема для обновления данных пользователя."""

    username: str

    first_name: str
    last_name: str
    full_name: str

    language: str = Field(max_length=3)
    is_active: bool
