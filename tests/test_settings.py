from pydantic_settings import SettingsConfigDict

from oltl import settings


class NestedSettings(settings.BaseSettings):
    nested_attr: str
    nested_numeric: float


class Settings(settings.BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OLTL_")
    nested: NestedSettings


def test_load_settings_with_settings1_json(settings1_json_path: str) -> None:

    with open(settings1_json_path, "r", encoding="utf-8") as fin:
        expected = Settings.model_validate_json(fin.read())

    actual = settings.load_settings(Settings, settings1_json_path)
    assert actual == expected


def test_load_settings_json_overrides_envvar(settings1_json_path: str, oltl_nested_settings_envvar: None) -> None:

    with open(settings1_json_path, "r", encoding="utf-8") as fin:
        expected = Settings.model_validate_json(fin.read())

    actual = settings.load_settings(Settings, settings1_json_path)
    assert actual == expected
    assert actual.nested.nested_attr == "nested_value"
    assert actual.nested.nested_numeric == 1.0


def test_load_settings_with_envvar(oltl_nested_settings_envvar: None) -> None:
    expected = Settings(nested=NestedSettings(nested_attr="environ_nested_attr", nested_numeric=-1.0))

    actual = settings.load_settings(Settings)
    assert actual == expected
    assert actual.nested.nested_attr == "environ_nested_attr"
    assert actual.nested.nested_numeric == -1.0
