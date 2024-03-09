import re


def test_oltl_has_version() -> None:
    import oltl

    assert re.match(r"\d+\.\d+\.\d+", oltl.__version__)
