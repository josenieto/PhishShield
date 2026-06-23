import pytest

from domain.services.homoglyphs.scripts import detect_unicode_scripts


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
