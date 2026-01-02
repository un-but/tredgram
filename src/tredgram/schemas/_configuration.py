"""Файл конфигурации всех частей приложения.

В модуле определена строгая иерархия, которой следует придерживаться.

Основный классом настроек является Config, для которого создается единственный экземпляр config,
который следует импортировать для доступа к конфигурации.

В классе Config все поля - классы pydantic, при инициализации в него нельзя передавать значения.

В Config все поля являются объектами в которых у всех полей должны быть значения
Field(json_schema_extra={"source": "ИСТОЧНИК_ПОЛЯ"})
"""

from __future__ import annotations

import os
import tomllib
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Literal, get_type_hints, override

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

if TYPE_CHECKING:
    from pydantic.fields import FieldInfo


def source(source: Literal["env", "toml"]) -> dict[str, dict[str, str]]:
    return {"json_schema_extra": {"source": source}}


########## Модели данных ##########


class BotConfig(PydanticBaseModel):
    """Настройка работы бота."""

    tg_token: SecretStr = Field(**source("env"))
    webhook_url: SecretStr = Field(**source("env"))

    min_send_interval: datetime = Field(**source("toml"))

    @field_validator("min_send_interval", mode="before")
    def parse_unix_timestamp(cls, value: Any) -> datetime:
        if isinstance(value, (str, int, float)):
            try:
                return timedelta(seconds=int(value))
            except (ValueError, TypeError):
                msg = f"Некорректный формат Unix timestamp: {value}"
                raise ValueError(msg)
        return value


class DatabaseConfig(PydanticBaseModel):
    """Настройки работы с базой данных через SQLAlchemy."""

    ps_url: SecretStr = Field(**source("env"))
    rd_url: SecretStr = Field(**source("env"))
    echo: bool = Field(**source("toml"))


########## Класс настроек ##########


class Config(BaseSettings):
    """Создает объект с настройками приложения."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot: BotConfig
    database: DatabaseConfig

    # Переопределение функции позволяет настроить получение значений из источников
    @classmethod
    @override
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Собирает кортеж настроенных источников, из которых берутся значения для конфигурации."""

        class TomlSource(PydanticBaseSettingsSource):
            @override
            def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
                return super().get_field_value(field, field_name)

            @override
            def __call__(self) -> dict[str, Any]:
                """Спарсить файл config.toml в словарь."""
                with Path("config.toml").open("rb") as f:
                    return tomllib.load(f)

        class EnvSource(PydanticBaseSettingsSource):
            @override
            def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
                return super().get_field_value(field, field_name)

            @override
            def __call__(self) -> dict[str, Any]:
                """Собрать все поля класса настроек и спарсить все подполя для них."""
                return {
                    field_name: self._parse_sub_fields_from_environment(field_name)
                    for field_name in settings_cls.model_fields
                }

            def _parse_sub_fields_from_environment(self, field_name: str) -> dict[str, Any]:
                """Спарсить все подполя из переменных окружения."""
                sub_fields: dict[str, Any] = {}
                field_class = get_type_hints(Config)[field_name]

                if not issubclass(field_class, PydanticBaseModel):
                    error_msg = "В классе Config указано поле, не являющееся схемой Pydantic"
                    raise TypeError(error_msg)

                # Перебор всех подполей их класса
                for sub_field_name, sub_field in field_class.model_fields.items():
                    env_name = f"{field_name}_{sub_field_name}".upper()
                    extra_data = sub_field.json_schema_extra

                    if not isinstance(extra_data, dict):
                        error_msg = f"В поле схемы {field_name} не был передан источник"
                        raise TypeError(error_msg)

                    if extra_data.get("source") == "env" and env_name in os.environ:
                        sub_fields[sub_field_name] = os.environ[env_name]

                return sub_fields

        return (EnvSource(settings_cls), TomlSource(settings_cls))


config = Config()
