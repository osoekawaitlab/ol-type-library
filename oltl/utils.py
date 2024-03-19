import re
import unicodedata

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
