import pytest

from domain.services.finding_analysis.finding_definitions import (
    build_finding_from_code,
    build_findings_from_codes,
)
from domain.value_objects.finding import (
    FINDING_CATEGORY_URL,
    FINDING_SEVERITY_HIGH,
    FINDING_SEVERITY_MEDIUM,
    Finding,
)


@pytest.mark.parametrize(
    ("code", "severity"),
    [
        ("URL_HAS_EMBEDDED_CREDENTIALS", FINDING_SEVERITY_HIGH),
        ("URL_SCHEME_NOT_ALLOWED", FINDING_SEVERITY_MEDIUM),
        ("URL_HAS_SUSPICIOUS_SCHEME", FINDING_SEVERITY_HIGH),
        ("URL_HAS_SUSPICIOUS_QUERY_DENSITY", FINDING_SEVERITY_MEDIUM),
        ("URL_USES_KNOWN_SHORTENER_DOMAIN", FINDING_SEVERITY_MEDIUM),
    ],
)
def test_should_build_url_finding_from_code(code: str, severity: str) -> None:
    finding = build_finding_from_code(code)

    assert finding == Finding(
        code=code,
        category=FINDING_CATEGORY_URL,
        severity=severity,
        explanation=finding.explanation,
    )
    assert finding.explanation != ""


def test_should_build_url_findings_from_codes_preserving_order() -> None:
    assert build_findings_from_codes(
        [
            "URL_SCHEME_NOT_ALLOWED",
            "URL_HAS_SUSPICIOUS_SCHEME",
            "URL_HAS_EMBEDDED_CREDENTIALS",
            "URL_HAS_SUSPICIOUS_QUERY_DENSITY",
            "URL_USES_KNOWN_SHORTENER_DOMAIN",
        ]
    ) == [
        Finding(
            code="URL_SCHEME_NOT_ALLOWED",
            category=FINDING_CATEGORY_URL,
            severity=FINDING_SEVERITY_MEDIUM,
            explanation="The URL uses a scheme outside the allowed set, which may indicate an unsafe or unexpected destination.",
        ),
        Finding(
            code="URL_HAS_SUSPICIOUS_SCHEME",
            category=FINDING_CATEGORY_URL,
            severity=FINDING_SEVERITY_HIGH,
            explanation="The URL uses a suspicious scheme that is not typical for normal web navigation.",
        ),
        Finding(
            code="URL_HAS_EMBEDDED_CREDENTIALS",
            category=FINDING_CATEGORY_URL,
            severity=FINDING_SEVERITY_HIGH,
            explanation="The URL includes embedded credentials, which can hide the real destination and mislead the user.",
        ),
        Finding(
            code="URL_HAS_SUSPICIOUS_QUERY_DENSITY",
            category=FINDING_CATEGORY_URL,
            severity=FINDING_SEVERITY_MEDIUM,
            explanation="The URL contains an unusually dense query string, which can be used to obfuscate tracking or malicious parameters.",
        ),
        Finding(
            code="URL_USES_KNOWN_SHORTENER_DOMAIN",
            category=FINDING_CATEGORY_URL,
            severity=FINDING_SEVERITY_MEDIUM,
            explanation="The URL uses a known shortening service, which can hide the final destination from the user.",
        ),
    ]
