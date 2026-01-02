"""Модуль включающий в себя все схемы. Для доступа следует импортировать схему из этого модуля."""

# pyright: reportUnusedImport=false
# ruff: noqa: F401, RUF100

from __future__ import annotations

from tredgram.schemas._common import SuccessResponse
from tredgram.schemas._configuration import Config, config

# __replace__ добавить model_rebuild в случае взаимных ссылок
# __replace__.model_rebuild()
