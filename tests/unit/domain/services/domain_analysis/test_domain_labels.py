import pytest

from domain.services.domain_analysis.domains import split_domain_labels


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
