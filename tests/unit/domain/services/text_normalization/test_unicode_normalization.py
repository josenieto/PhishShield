import pytest

from domain.services.text_normalization.unicode_text import normalize_unicode_text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("ＡＢＣ", "ABC"),
        ("１２３", "123"),
        ("ℌ𝔢𝔩𝔩𝔬", "Hello"),
        ("hello", "hello"),
        ("café", "café"),
        ("", ""),
    ],
)
def test_should_normalize_unicode_text(text: str, expected: str) -> None:
    assert normalize_unicode_text(text) == expected
