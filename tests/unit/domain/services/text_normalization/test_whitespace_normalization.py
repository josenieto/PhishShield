import pytest

from domain.services.text_normalization.whitespace import normalize_whitespace


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("hello    world", "hello world"),
        ("hello\t\tworld", "hello world"),
        ("hello \t  world", "hello world"),
        ("  hello world  ", "hello world"),
        ("hello\n\nworld", "hello world"),
        ("hello world", "hello world"),
        ("", ""),
        ("   \t\n  ", ""),
    ],
)
def test_should_normalize_whitespace(text: str, expected: str) -> None:
    assert normalize_whitespace(text) == expected
