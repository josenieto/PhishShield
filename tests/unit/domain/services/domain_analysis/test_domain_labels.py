import pytest

from domain.services.domain_analysis.domains import (
    contains_punycode,
    is_punycode_label,
    split_domain_labels,
)


@pytest.mark.parametrize(
    ("domain", "expected"),
    [
        ("login.example.com", ["login", "example", "com"]),
        ("example.com.", ["example", "com"]),
        (" login.example.com ", ["login", "example", "com"]),
        ("login..example.com", ["login", "example", "com"]),
        ("", []),
        ("   ", []),
    ],
)
def test_should_split_domain_labels(domain: str, expected: list[str]) -> None:
    assert split_domain_labels(domain) == expected


@pytest.mark.parametrize(
    "label",
    [
        "xn--example",
        "xn--paypl-3ve",
        "XN--EXAMPLE",
    ],
)
def test_should_detect_punycode_label(label: str) -> None:
    assert is_punycode_label(label) is True


@pytest.mark.parametrize(
    "label",
    [
        "example",
        "paypl",
        "",
        " xn--example",
        "example-xn--",
    ],
)
def test_should_return_false_for_non_punycode_label(label: str) -> None:
    assert is_punycode_label(label) is False


@pytest.mark.parametrize(
    "domain",
    [
        "xn--paypl-3ve.com",
        "login.xn--example.com",
        "XN--EXAMPLE.com",
    ],
)
def test_should_detect_domain_with_punycode_label(domain: str) -> None:
    assert contains_punycode(domain) is True


@pytest.mark.parametrize(
    "domain",
    [
        "example.com",
        "",
        "   ",
        "example-xn--.com",
    ],
)
def test_should_return_false_when_domain_has_no_punycode_label(domain: str) -> None:
    assert contains_punycode(domain) is False
