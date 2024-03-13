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
    newline_to_space: bool = False,
    remove_multiple_spaces: bool = False,
    remove_variation_selectors: bool = False,
) -> str:
    normalized_string = parentheses_right.sub(
        r") \1", parentheses_left.sub(r"\1 (", unicodedata.normalize("NFKC", x).translate(normalize_trans_map))
    )
    if newline_to_space:
        normalized_string = re.sub(r"[\n\r]", " ", normalized_string)
    if remove_multiple_spaces:
        normalized_string = re.sub(r" +", " ", normalized_string)
    if remove_variation_selectors:
        normalized_string = re.sub(r"[\U000e0100-\U000e01ef]", "", normalized_string)
    return normalized_string
