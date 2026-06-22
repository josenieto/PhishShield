import pytest

from domain.services.text_normalization.invisible_characters import (
    contains_invisible_chars,
    strip_invisible_chars,
)


@pytest.mark.parametrize(
    "text",
    [
        "paypa\u200bl.com",
        "micro\u200csoft.com",
        "veri\u200dfy",
    ],
)
def test_should_detect_invisible_characters(text: str) -> None:
    assert contains_invisible_chars(text) is True


@pytest.mark.parametrize(
    "text",
    [
        "paypal.com",
        "safe text",
        "",
    ],
)
def test_should_return_false_when_text_has_no_invisible_characters(text: str) -> None:
    assert contains_invisible_chars(text) is False


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("paypa\u200bl.com", "paypal.com"),
        ("micro\u200csoft.com", "microsoft.com"),
        ("veri\u200dfy", "verify"),
        ("a\u200bb\u200cc\u200d", "abc"),
    ],
)
def test_should_strip_invisible_characters(text: str, expected: str) -> None:
    assert strip_invisible_chars(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "paypal.com",
        "safe text",
        "",
    ],
)
def test_should_preserve_text_without_invisible_characters(text: str) -> None:
    assert strip_invisible_chars(text) == text