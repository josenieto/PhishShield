import pytest

from domain.services.homoglyphs.scripts import (
    contains_mixed_scripts,
    detect_unicode_scripts,
)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("microsoft", {"LATIN"}),
        ("пример", {"CYRILLIC"}),
        ("δοκιμή", {"GREEK"}),
        ("microsоft", {"LATIN", "CYRILLIC"}),
        ("microsoft-365.com", {"LATIN"}),
        ("123-._", set()),
        ("", set()),
    ],
)
def test_should_detect_unicode_scripts(text: str, expected: set[str]) -> None:
    assert detect_unicode_scripts(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("microsoft.com", False),
        ("microsоft.com", True),
        ("paypαl.com", True),
        ("пример", False),
        ("δοκιμή", False),
        ("paypal-365.com", False),
        ("123-._", False),
        ("", False),
    ],
)
def test_should_detect_mixed_unicode_scripts(text: str, expected: bool) -> None:
    assert contains_mixed_scripts(text) is expected
