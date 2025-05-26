import pytest

from oltl import utils


@pytest.mark.parametrize(
    ["raw", "expected"],
    [
        ["\u0020\u00a0\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u200a\u200b\u3000\ufeff\u0009", "              "],
        ["\u30b9\u3099", "ズ"],
        ["ｾﾞﾝｶｸｶﾅ", "ゼンカクカナ"],
        ["！？＠＃“”‘’", "!?@#\"\"''"],
        ["「・」", "「・」"],
        ["˗֊‐‑‒–⁃⁻₋−", "----------"],
        ["Ｈａｌｆ　Ｗｉｄｔｈ", "Half Width"],
        ["~〜", "~〜"],
        ["１月", "1月"],
        ["\u2fa6", "金"],
        ["単語（たんご）と括弧（かっこ）の間にスペース", "単語 (たんご) と括弧 (かっこ) の間にスペース"],
        ["(x) (y)", "(x) (y)"],
        ["((x))", "((x))"],
        ["o(x)  (y)", "o (x)  (y)"],
    ],
)
def test_normalize_default(raw: str, expected: str) -> None:
    actual = utils.normalize_jptext(raw)
    assert actual == expected
