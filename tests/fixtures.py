from pydantic import ValidationError

from oltl import core

string_test_cases = [
    (
        (core.LimitedMinLengthMixin,),
        (
            (
                "a",
                ValidationError.from_exception_data(
                    title="TestModel",
                    line_errors=[
                        {
                            "loc": ("name",),
                            "type": "string_too_short",
                            "ctx": {"min_length": 3},
                            "input": "a",
                        }
                    ],
                ),
            ),
            ("abc", "abc"),
            ("abcde", "abcde"),
        ),
    ),
]
