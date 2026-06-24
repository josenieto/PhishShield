import pytest

from domain.services.url_analysis.schemes import (
    is_suspicious_url_scheme,
    is_url_scheme_allowed,
)


@pytest.mark.parametrize(
    ("scheme", "allowed_schemes"),
    [
        ("http", {"http", "https", "mailto"}),
        ("https", {"http", "https", "mailto"}),
        ("mailto", {"http", "https", "mailto"}),
        ("HTTPS", {"https"}),
        (" https ", {"https"}),
    ],
)
def test_should_detect_allowed_url_scheme(
    scheme: str,
    allowed_schemes: set[str],
) -> None:
    assert is_url_scheme_allowed(scheme, allowed_schemes) is True


@pytest.mark.parametrize(
    ("scheme", "allowed_schemes"),
    [
        ("javascript", {"http", "https"}),
        ("", {"http", "https"}),
        ("   ", {"http", "https"}),
        ("https", set()),
    ],
)
def test_should_return_false_when_url_scheme_is_not_allowed(
    scheme: str,
    allowed_schemes: set[str],
) -> None:
    assert is_url_scheme_allowed(scheme, allowed_schemes) is False


@pytest.mark.parametrize(
    "scheme",
    [
        "javascript",
        "data",
        "file",
        "vbscript",
        "JAVASCRIPT",
        " data ",
    ],
)
def test_should_detect_suspicious_url_scheme(scheme: str) -> None:
    assert is_suspicious_url_scheme(scheme) is True


@pytest.mark.parametrize(
    "scheme",
    [
        "http",
        "https",
        "mailto",
        "",
        "   ",
    ],
)
def test_should_return_false_when_url_scheme_is_not_suspicious(scheme: str) -> None:
    assert is_suspicious_url_scheme(scheme) is False
