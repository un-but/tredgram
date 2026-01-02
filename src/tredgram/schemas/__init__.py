"""Модуль включающий в себя все схемы. Для доступа следует импортировать схему из этого модуля."""

# pyright: reportUnusedImport=false
# ruff: noqa: F401, RUF100

from __future__ import annotations

from tredgram.schemas._common import USER_INCLUDE_TYPE, SuccessResponse
from tredgram.schemas._configuration import Config, config
from tredgram.schemas.post import PostChildResponse, PostCreate, PostResponse, PostUpdate
from tredgram.schemas.user import UserCreate, UserResponse, UserUpdate

UserResponse.model_rebuild()
