import re
import unicodedata
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, Literal, Type

from pydantic_settings import BaseSettings

normalize_trans_map = str.maketrans(
    {
        "˗": "-",
        "֊": "-",
        "‐": "-",
        "‑": "-",
        "‒": "-",
        "–": "-",
        "⁃": "-",
        "⁻": "-",
        "₋": "-",
        "−": "-",
        "　": " ",
        "\u200b": " ",
        "\ufeff": " ",
        "\t": " ",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
    }
)

parentheses_left = re.compile(r"([^\s(])\(")
parentheses_right = re.compile(r"\)([^\s)])")


def normalize_jptext(
    x: str,
) -> str:
    normalized_string = parentheses_right.sub(
        r") \1", parentheses_left.sub(r"\1 (", unicodedata.normalize("NFKC", x).translate(normalize_trans_map))
    )
    return normalized_string


@contextmanager
def patch_config_value(
    cls: Type[BaseSettings],
    key: Literal["json_file", "yaml_file"],
    value: Any,
) -> Generator[None, None, None]:
    old_value = cls.model_config[key]
    cls.model_config[key] = value
    yield
    cls.model_config[key] = old_value
