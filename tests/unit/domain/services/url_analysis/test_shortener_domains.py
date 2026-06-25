import pytest

from domain.services.url_analysis.shorteners import has_url_shortener_domain


@pytest.mark.parametrize(
    ("domain", "known_shorteners"),
    [
        ("bit.ly", {"bit.ly"}),
        ("BIT.LY", {"bit.ly"}),
        ("bit.ly.", {"bit.ly"}),
        ("tinyurl.com", {"tinyurl.com"}),
        ("tinyurl.com", {"tinyurl.com."}),
    ],
)
def test_should_detect_known_url_shortener_domain(
    domain: str,
    known_shorteners: set[str],
) -> None:
    assert has_url_shortener_domain(domain, known_shorteners) is True


@pytest.mark.parametrize(
    ("domain", "known_shorteners"),
    [
        ("example.com", {"bit.ly"}),
        ("sub.bit.ly", {"bit.ly"}),
        ("bit.ly", set()),
        ("", {"bit.ly"}),
        ("   ", {"bit.ly"}),
    ],
)
def test_should_return_false_when_domain_is_not_a_known_url_shortener(
    domain: str,
    known_shorteners: set[str],
) -> None:
    assert has_url_shortener_domain(domain, known_shorteners) is False
