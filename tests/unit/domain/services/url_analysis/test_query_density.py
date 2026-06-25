import pytest

from domain.services.url_analysis.query import has_suspicious_query_density


@pytest.mark.parametrize(
    ("url", "threshold"),
    [
        ("https://example.com", 3),
        ("https://example.com?a=1", 3),
        ("https://example.com?a=1&b=2&c=3", 3),
        ("", 3),
        ("   ", 3),
        ("https://[invalid?a=1&b=2", 1),
    ],
)
def test_should_return_false_when_query_density_is_not_suspicious(
    url: str,
    threshold: int,
) -> None:
    assert has_suspicious_query_density(url, threshold) is False


@pytest.mark.parametrize(
    ("url", "threshold"),
    [
        ("https://example.com?a=1&b=2&c=3&d=4", 3),
        ("https://example.com?a=1&b=2", 1),
        ("https://example.com?a=1&a=2", 1),
    ],
)
def test_should_detect_suspicious_query_density(
    url: str,
    threshold: int,
) -> None:
    assert has_suspicious_query_density(url, threshold) is True
