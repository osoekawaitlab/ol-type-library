import os
from collections.abc import Generator

from pytest import fixture
from pytest_mock import MockerFixture


@fixture
def test_dir() -> Generator[str, None, None]:
    yield os.path.abspath(os.path.dirname(__file__))


@fixture
def fixtures_dir(test_dir: str) -> Generator[str, None, None]:
    yield os.path.join(test_dir, "fixtures")


@fixture
def settings1_json_path(fixtures_dir: str) -> Generator[str, None, None]:
    yield os.path.join(fixtures_dir, "settings1.json")


@fixture
def oltl_nested_settings_envvar(mocker: MockerFixture) -> Generator[None, None, None]:
    mocker.patch.dict(
        os.environ,
        {
            "OLTL_NESTED__NESTED_ATTR": "environ_nested_attr",
            "OLTL_NESTED__NESTED_NUMERIC": "-1.0",
        },
    )
    yield
