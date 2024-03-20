import re

import oltl


def test_oltl_has_version() -> None:

    assert re.match(r"\d+\.\d+\.\d+", oltl.__version__)


def test_oltl_has_id() -> None:
    expected = "01HRQ0BNKS4WMFVQPW810MPM3V"
    actual = oltl.Id("01HRQ0BNKS4WMFVQPW810MPM3V")
    assert actual.str == expected


def test_oltl_has_timestamp() -> None:
    expected = 1627574400000000
    actual = oltl.Timestamp("2021-07-29T16:00:00Z")
    assert actual == expected


def test_oltl_has_type_string() -> None:
    expected = "snake_case_in_python_camel_case_in_json"
    actual = oltl.TypeString.from_str("snake_case_in_python_camel_case_in_json")
    assert actual == expected
