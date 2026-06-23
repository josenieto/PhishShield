import pytest

from domain.services.homoglyphs.confusables import (
    contains_confusable_characters,
    find_confusable_characters,
)


@pytest.mark.parametrize(
    "text",
    [
        "microsоft.com",
        "pаypal.com",
        "paypαl.com",
        "gοοgle.com",
    ],
)
def test_should_detect_confusable_characters(text: str) -> None:
    assert contains_confusable_characters(text) is True


@pytest.mark.parametrize(
    "text",
    [
        "microsoft.com",
        "paypal.com",
        "google.com",
        "123-._",
        "",
    ],
)
def test_should_return_false_when_text_has_no_confusable_characters(text: str) -> None:
    assert contains_confusable_characters(text) is False


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("microsоft.com", ["о"]),
        ("pаypαl.com", ["а", "α"]),
        ("gοοgle.com", ["ο", "ο"]),
        ("paypal.com", []),
        ("", []),
    ],
)
def test_should_find_confusable_characters_in_discovery_order(
    text: str,
    expected: list[str],
) -> None:
    assert find_confusable_characters(text) == expected
