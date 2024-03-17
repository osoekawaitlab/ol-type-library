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


class LimitedMinMaxLength(core.LimitedMinLengthMixin, core.LimitedMaxLengthMixin):
    @classmethod
    def get_min_length(cls) -> int:
        return 3

    @classmethod
    def get_max_length(cls) -> int:
        return 4


class Normalized(core.NormalizedStringMixin):
    pass


class NormalizedMinLength(core.NormalizedStringMixin, core.LimitedMinLengthMixin):
    @classmethod
    def get_min_length(cls) -> int:
        return 3


class NormalizedMaxLength(core.NormalizedStringMixin, core.LimitedMaxLengthMixin):
    @classmethod
    def get_max_length(cls) -> int:
        return 4


class Trimmed(core.TrimmedStringMixin):
    pass


class TrimmedNonEmpty(core.TrimmedStringMixin, core.NonEmptyStringMixin):
    pass


class TrimmedMinLength(core.TrimmedStringMixin, core.LimitedMinLengthMixin):
    @classmethod
    def get_min_length(cls) -> int:
        return 3


class TrimmedMaxLength(core.TrimmedStringMixin, core.LimitedMaxLengthMixin):
    @classmethod
    def get_max_length(cls) -> int:
        return 4


class TrimmedNormalized(core.TrimmedStringMixin, core.NormalizedStringMixin):
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
            ("ﾊﾞﾋﾞ", "ﾊﾞﾋﾞ"),
            (
                "バビ",
                ValidationError.from_exception_data(
                    title="TestModel",
                    line_errors=[
                        {
                            "loc": ("value",),
                            "type": "string_too_short",
                            "ctx": {"min_length": 3},
                            "input": "バビ",
                        }
                    ],
                ),
            ),
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
            (
                "ﾊﾞﾋﾞﾌﾞ",
                ValidationError.from_exception_data(
                    title="TestModel",
                    line_errors=[
                        {
                            "loc": ("value",),
                            "type": "string_too_long",
                            "ctx": {"max_length": 4},
                            "input": "ﾊﾞﾋﾞﾌﾞ",
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
    (
        LimitedMinMaxLength,
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
            ("abcd", "abcd"),
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
        Normalized,
        (
            (
                "already normalized",
                "already normalized",
            ),
            (
                "　　not　normalized　　",
                "  not normalized  ",
            ),
            ("ﾊﾞﾋﾞﾌﾞﾍﾞﾎﾞ", "バビブベボ"),
        ),
    ),
    (
        NormalizedMinLength,
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
            (
                "　　not　normalized　　",
                "  not normalized  ",
            ),
            (
                "バビ",
                ValidationError.from_exception_data(
                    title="TestModel",
                    line_errors=[
                        {
                            "loc": ("value",),
                            "type": "string_too_short",
                            "ctx": {"min_length": 3},
                            "input": "バビ",
                        }
                    ],
                ),
            ),
            (
                "ﾊﾞﾋﾞ",
                ValidationError.from_exception_data(
                    title="TestModel",
                    line_errors=[
                        {
                            "loc": ("value",),
                            "type": "string_too_short",
                            "ctx": {"min_length": 3},
                            "input": "バビ",
                        }
                    ],
                ),
            ),
        ),
    ),
    (
        NormalizedMaxLength,
        (
            ("a", "a"),
            (
                "　a　",
                " a ",
            ),
            ("ﾊﾞﾋﾞﾌﾞ", "バビブ"),
            (
                "　　　　　",
                ValidationError.from_exception_data(
                    title="TestModel",
                    line_errors=[
                        {
                            "loc": ("value",),
                            "type": "string_too_long",
                            "ctx": {"max_length": 4},
                            "input": "     ",
                        }
                    ],
                ),
            ),
        ),
    ),
    (
        Trimmed,
        (
            (
                "already trimmed",
                "already trimmed",
            ),
            (
                "　　not　trimmed　　",
                "not　trimmed",
            ),
            ("ﾊﾞﾋﾞﾌﾞﾍﾞﾎﾞ", "ﾊﾞﾋﾞﾌﾞﾍﾞﾎﾞ"),
        ),
    ),
    (
        TrimmedNonEmpty,
        (
            (
                "    ",
                ValidationError.from_exception_data(
                    title="TestModel",
                    line_errors=[
                        {
                            "loc": ("value",),
                            "type": "string_too_short",
                            "ctx": {"min_length": 1},
                            "input": "    ",
                        }
                    ],
                ),
            ),
            (
                "　　not　trimmed　　",
                "not　trimmed",
            ),
            (
                "ﾊﾞﾋﾞﾌﾞﾍﾞﾎﾞ",
                "ﾊﾞﾋﾞﾌﾞﾍﾞﾎﾞ",
            ),
        ),
    ),
    (
        TrimmedMinLength,
        (
            (
                "  a  ",
                ValidationError.from_exception_data(
                    title="TestModel",
                    line_errors=[
                        {
                            "loc": ("value",),
                            "type": "string_too_short",
                            "ctx": {"min_length": 3},
                            "input": "  a  ",
                        }
                    ],
                ),
            ),
            (
                "　　not　trimmed　　",
                "not　trimmed",
            ),
            (
                "ﾊﾞﾋﾞﾌﾞﾍﾞﾎﾞ",
                "ﾊﾞﾋﾞﾌﾞﾍﾞﾎﾞ",
            ),
        ),
    ),
    (
        TrimmedMaxLength,
        (
            ("a", "a"),
            (
                "　a　",
                "a",
            ),
            (
                "　zz　z　　　",
                "zz　z",
            ),
        ),
    ),
    (
        TrimmedNormalized,
        (
            (
                "already trimmed and normalized",
                "already trimmed and normalized",
            ),
            (
                "　　not　trimmed　　",
                "not trimmed",
            ),
            (
                " ﾊﾞ ﾋﾞ ﾌﾞ ﾍﾞ ﾎﾞ ",
                "バ ビ ブ ベ ボ",
            ),
        ),
    ),
]
