from typing import Optional, Type, TypeVar

from pydantic import Field, FilePath
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import (
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from .utils import patch_config_value

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

    model_config = SettingsConfigDict(env_file_encoding="utf-8", env_nested_delimiter="__")

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
            JsonConfigSettingsSource(settings_cls),
            YamlConfigSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    @classmethod
    def load(cls: Type[SettingsClassT], setting_file_path: Optional[str] = None) -> SettingsClassT:
        if setting_file_path is not None:
            if setting_file_path.endswith(".json"):
                with patch_config_value(cls, "json_file", setting_file_path):
                    return cls()
            if setting_file_path.endswith(".yaml") or setting_file_path.endswith(".yml"):
                with patch_config_value(cls, "yaml_file", setting_file_path):
                    return cls()
        return cls()
