from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict


class BaseSettings(PydanticBaseSettings):
    """Base settings for the application.

    This class is used as a base class for handling miscellaneous settings.
    The child classes will support setting values via environment variables even nested ones.


    >>> from oltl.settings import BaseSettings
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
    """

    model_config = SettingsConfigDict(env_file_encoding="utf-8", env_nested_delimiter="__")
