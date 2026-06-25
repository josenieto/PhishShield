import pytest

from domain.services.url_analysis.credentials import has_embedded_credentials


@pytest.mark.parametrize(
    "url",
    [
        "https://user@example.com",
        "https://user:password@example.com",
        "http://admin@example.org/login",
        "HTTPS://USER:PASS@EXAMPLE.COM",
    ],
)
def test_should_detect_url_with_embedded_credentials(url: str) -> None:
    assert has_embedded_credentials(url) is True


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com",
        "https://example.com/path@value",
        "https://example.com/search?q=user@example.com",
        "mailto:user@example.com",
        "not a url",
        "https://[invalid",
        "",
        "   ",
    ],
)
def test_should_return_false_when_url_has_no_embedded_credentials(url: str) -> None:
    assert has_embedded_credentials(url) is False
