from pydantic import ValidationError

from oltl import core


class LimitedMinLength(core.LimitedMinLengthMixin):
    @classmethod
    def get_min_length(cls) -> int:
        return 3


class LimitedMaxLength(core.LimitedMaxLengthMixin):
    @classmethod
    def get_max_length(cls) -> int:
        return 4


class NonEmpty(core.NonEmptyStringMixin):
    pass


string_test_cases = [
    (
        LimitedMinLength,
        (
            (
                "a",
                ValidationError.from_exception_data(
                    title="TestModel",
                    line_errors=[
                        {
                            "loc": ("value",),
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
    (
        LimitedMaxLength,
        (
            ("a", "a"),
            ("abc", "abc"),
            (
                "abcde",
                ValidationError.from_exception_data(
                    title="TestModel",
                    line_errors=[
                        {
                            "loc": ("value",),
                            "type": "string_too_long",
                            "ctx": {"max_length": 4},
                            "input": "abcde",
                        }
                    ],
                ),
            ),
        ),
    ),
    (
        NonEmpty,
        (
            (
                "",
                ValidationError.from_exception_data(
                    title="TestModel",
                    line_errors=[
                        {
                            "loc": ("value",),
                            "type": "string_too_short",
                            "ctx": {"min_length": 1},
                            "input": "",
                        }
                    ],
                ),
            ),
            ("a", "a"),
        ),
    ),
]
