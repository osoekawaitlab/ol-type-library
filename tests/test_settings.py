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

    actual = Settings.load(settings1_json_path)
    assert actual == expected


def test_load_settings_json_overrides_envvar(settings1_json_path: str, oltl_nested_settings_envvar: None) -> None:

    with open(settings1_json_path, "r", encoding="utf-8") as fin:
        expected = Settings.model_validate_json(fin.read())

    actual = Settings.load(settings1_json_path)
    assert actual == expected
    assert actual.nested.nested_attr == "nested_value"
    assert actual.nested.nested_numeric == 1.0


def test_load_settings_with_envvar(oltl_nested_settings_envvar: None) -> None:
    expected = Settings(nested=NestedSettings(nested_attr="environ_nested_attr", nested_numeric=-1.0))

    actual = Settings.load()
    assert actual == expected
    assert actual.nested.nested_attr == "environ_nested_attr"
    assert actual.nested.nested_numeric == -1.0


def test_load_settings_with_settings_yml(settings_yml_path: str) -> None:

    actual = Settings.load(settings_yml_path)
    expected = Settings(nested=NestedSettings(nested_attr="value_from_yml", nested_numeric=2.0))
    assert actual == expected


def test_load_settings_with_settings_yaml(settings_yaml_path: str) -> None:

    actual = Settings.load(settings_yaml_path)
    expected = Settings(nested=NestedSettings(nested_attr="value_from_yaml", nested_numeric=3.0))
    assert actual == expected
