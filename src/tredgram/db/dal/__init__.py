"""Модуль для работы с моделями ORM. Рекомендую импортировать напрямую из этого модуля модели."""

# pyright: reportUnusedImport=false
# ruff: noqa: F401, RUF100

from __future__ import annotations

from __replace__.db.dal.post import PostDAL
from __replace__.db.dal.user import UserDAL
