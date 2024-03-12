import re

import oltl


def test_oltl_has_version() -> None:

    assert re.match(r"\d+\.\d+\.\d+", oltl.__version__)


def test_oltl_has_id() -> None:
    expected = "01HRQ0BNKS4WMFVQPW810MPM3V"
    actual = oltl.Id("01HRQ0BNKS4WMFVQPW810MPM3V")
    assert actual.str == expected
