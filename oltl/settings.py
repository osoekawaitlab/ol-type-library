from typing import Optional, Type, TypeVar

from pydantic import Field, FilePath
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import (
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

SettingsClassT = TypeVar("SettingsClassT", bound="BaseSettings")


class BaseSettings(PydanticBaseSettings):
    """Base settings for the application.

    This class is used as a base class for handling miscellaneous settings.
    The child classes will support setting values via environment variables even nested ones.


    >>> class SomeSettings(BaseSettings):
    ...     some_value: str
    ...
    >>> class SomeNestedSettings(BaseSettings):
    ...     some_nested_value: SomeSettings
    ...
    >>> import os
    >>> from unittest.mock import patch
    >>> with patch.dict(os.environ, {"SOME_NESTED_VALUE__SOME_VALUE": "value"}):
    ...     settings = SomeNestedSettings()
    >>> settings.some_nested_value.some_value
    'value'
    >>> settings.model_dump_json()
    '{"some_nested_value":{"some_value":"value"}}'
    """

    model_config = SettingsConfigDict(env_file_encoding="utf-8", env_nested_delimiter="__", frozen=False)

    config_path: Optional[FilePath] = Field(default=None, exclude=True)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[PydanticBaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            JsonConfigSettingsSource(settings_cls),
        )


def load_settings(setting_cls: Type[SettingsClassT], json_file_path: str) -> SettingsClassT:
    setting_cls.model_config["json_file"] = json_file_path
    return setting_cls()
