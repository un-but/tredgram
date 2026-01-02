"""Схемы для работы с постами."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import Field
from tredgram.schemas._common import BaseSchema

if TYPE_CHECKING:  # Требуется для корректной работы отложенного импорта
    from tredgram.schemas import UserResponse


class PostBase(BaseSchema):
    """Базовая схема публикации."""

    id: int
    content: str


class PostCreate(PostBase):
    """Схема для создания публикации."""


class PostChildResponse(PostBase):
    """Схема для ответа в качестве дочернего объекта."""

    created_at: datetime


class PostResponse(PostBase):
    """Схема для ответа с данными публикации."""

    user: UserResponse


class PostUpdate(BaseSchema):
    """Схема для обновления данных публикации."""

    content: str
