from pydantic import ValidationError

from oltl import core


class LimitedMinLength(core.LimitedMinLengthStringMixIn):
    @classmethod
    def get_min_length(cls) -> int:
        return 3


class LimitedMaxLength(core.LimitedMaxLengthStringMixIn):
    @classmethod
    def get_max_length(cls) -> int:
        return 4


class NonEmpty(core.NonEmptyStringMixIn):
    pass


class LimitedMinMaxLength(core.LimitedMinLengthStringMixIn, core.LimitedMaxLengthStringMixIn):
    @classmethod
    def get_min_length(cls) -> int:
        return 3

    @classmethod
    def get_max_length(cls) -> int:
        return 4


class Normalized(core.NormalizedStringMixIn):
    pass


class NormalizedMinLength(core.NormalizedStringMixIn, core.LimitedMinLengthStringMixIn):
    @classmethod
    def get_min_length(cls) -> int:
        return 3


class NormalizedMaxLength(core.NormalizedStringMixIn, core.LimitedMaxLengthStringMixIn):
    @classmethod
    def get_max_length(cls) -> int:
        return 4


class Trimmed(core.TrimmedStringMixIn):
    pass


class TrimmedNonEmpty(core.TrimmedStringMixIn, core.NonEmptyStringMixIn):
    pass


class TrimmedMinLength(core.TrimmedStringMixIn, core.LimitedMinLengthStringMixIn):
    @classmethod
    def get_min_length(cls) -> int:
        return 3


class TrimmedMaxLength(core.TrimmedStringMixIn, core.LimitedMaxLengthStringMixIn):
    @classmethod
    def get_max_length(cls) -> int:
        return 4


class TrimmedNormalized(core.TrimmedStringMixIn, core.NormalizedStringMixIn):
    pass


class SnakeCase(core.SnakeCaseStringMixIn):
    pass


class NormalizedSnakeCase(core.NormalizedStringMixIn, core.SnakeCaseStringMixIn):
    pass


class SnakeCaseNormalized(core.SnakeCaseStringMixIn, core.NormalizedStringMixIn):
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
                " not trimmed and ｎｏｔ　ｎｏｒｍａｌｉｚｅｄ　 \t",
                "not trimmed and not normalized",
            ),
            (
                " ﾊﾞ ﾋﾞ ﾌﾞ ﾍﾞ ﾎﾞ ",
                "バ ビ ブ ベ ボ",
            ),
        ),
    ),
    (
        SnakeCase,
        (
            (
                "already_snake_case",
                "already_snake_case",
            ),
            (
                "camelCase",
                "camel_case",
            ),
            (
                "PascalCase",
                "pascal_case",
            ),
            (
                "kebab-case",
                "kebab_case",
            ),
            ("UPPER_CASE", "upper_case"),
            (
                "ｱｲｳｴｵ",
                "ｱｲｳｴｵ",
            ),
            (
                "ｓＮｅａｋ＿ｃａｓｅ",
                "ｓｎｅａｋ＿ｃａｓｅ",
            ),
        ),
    ),
    (
        NormalizedSnakeCase,
        (
            (
                "ｎｏｔＮｏｒｍａｌｉｚｅｄCamelCase",
                "not_normalized_camel_case",
            ),
            (
                "  ﾉｰﾏﾗｲｽﾞ　ｻﾚﾃｲﾅｲ PascalCase  ",
                "  ノーマライズ サレテイナイ pascal_case  ",
            ),
        ),
    ),
    (
        SnakeCaseNormalized,
        (
            (
                "ｎｏｔＮｏｒｍａｌｉｚｅｄCamelCase",
                "notnormalizedcamel_case",
            ),
            (
                "  ﾉｰﾏﾗｲｽﾞ　ｻﾚﾃｲﾅｲ PascalCase  ",
                "  ノーマライズ サレテイナイ pascal_case  ",
            ),
        ),
    ),
]


class UpperAndLowerBoundInteger(core.UpperBoundIntegerMixIn, core.LowerBoundIntegerMixIn):
    @classmethod
    def get_min_value(cls) -> int:
        return 3

    @classmethod
    def get_max_value(cls) -> int:
        return 5


integer_test_cases = [
    (
        UpperAndLowerBoundInteger,
        (
            (
                2,
                ValidationError.from_exception_data(
                    title="TestModel",
                    line_errors=[
                        {
                            "loc": ("value",),
                            "type": "greater_than_equal",
                            "ctx": {"ge": 3},
                            "input": 2,
                        }
                    ],
                ),
            ),
            (3, 3),
            (4, 4),
            (5, 5),
            (
                6,
                ValidationError.from_exception_data(
                    title="TestModel",
                    line_errors=[
                        {
                            "loc": ("value",),
                            "type": "less_than_equal",
                            "ctx": {"le": 5},
                            "input": 6,
                        }
                    ],
                ),
            ),
        ),
    ),
]


class UpperAndLowerBoundFloat(core.UpperBoundFloatMixIn, core.LowerBoundFloatMixIn):
    @classmethod
    def get_min_value(cls) -> float:
        return 3.0

    @classmethod
    def get_max_value(cls) -> float:
        return 5.0


float_test_cases = [
    (
        UpperAndLowerBoundFloat,
        (
            (
                2.9,
                ValidationError.from_exception_data(
                    title="TestModel",
                    line_errors=[
                        {
                            "loc": ("value",),
                            "type": "greater_than_equal",
                            "ctx": {"ge": 3.0},
                            "input": 2.9,
                        }
                    ],
                ),
            ),
            (3.0, 3.0),
            (4.0, 4.0),
            (5.0, 5.0),
            (
                5.1,
                ValidationError.from_exception_data(
                    title="TestModel",
                    line_errors=[
                        {
                            "loc": ("value",),
                            "type": "less_than_equal",
                            "ctx": {"le": 5.0},
                            "input": 5.1,
                        }
                    ],
                ),
            ),
        ),
    ),
]
