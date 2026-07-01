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


def test_should_build_known_url_finding_from_code() -> None:
    assert build_finding_from_code("URL_HAS_EMBEDDED_CREDENTIALS") == Finding(
        code="URL_HAS_EMBEDDED_CREDENTIALS",
        category=FINDING_CATEGORY_URL,
        severity=FINDING_SEVERITY_HIGH,
    )


def test_should_build_url_scheme_not_allowed_finding_from_code() -> None:
    assert build_finding_from_code("URL_SCHEME_NOT_ALLOWED") == Finding(
        code="URL_SCHEME_NOT_ALLOWED",
        category=FINDING_CATEGORY_URL,
        severity=FINDING_SEVERITY_MEDIUM,
    )


def test_should_build_suspicious_url_scheme_finding_from_code() -> None:
    assert build_finding_from_code("URL_HAS_SUSPICIOUS_SCHEME") == Finding(
        code="URL_HAS_SUSPICIOUS_SCHEME",
        category=FINDING_CATEGORY_URL,
        severity=FINDING_SEVERITY_HIGH,
    )


def test_should_build_suspicious_url_query_density_finding_from_code() -> None:
    assert build_finding_from_code("URL_HAS_SUSPICIOUS_QUERY_DENSITY") == Finding(
        code="URL_HAS_SUSPICIOUS_QUERY_DENSITY",
        category=FINDING_CATEGORY_URL,
        severity=FINDING_SEVERITY_MEDIUM,
    )


def test_should_build_known_url_shortener_finding_from_code() -> None:
    assert build_finding_from_code("URL_USES_KNOWN_SHORTENER_DOMAIN") == Finding(
        code="URL_USES_KNOWN_SHORTENER_DOMAIN",
        category=FINDING_CATEGORY_URL,
        severity=FINDING_SEVERITY_MEDIUM,
    )


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
        ),
        Finding(
            code="URL_HAS_SUSPICIOUS_SCHEME",
            category=FINDING_CATEGORY_URL,
            severity=FINDING_SEVERITY_HIGH,
        ),
        Finding(
            code="URL_HAS_EMBEDDED_CREDENTIALS",
            category=FINDING_CATEGORY_URL,
            severity=FINDING_SEVERITY_HIGH,
        ),
        Finding(
            code="URL_HAS_SUSPICIOUS_QUERY_DENSITY",
            category=FINDING_CATEGORY_URL,
            severity=FINDING_SEVERITY_MEDIUM,
        ),
        Finding(
            code="URL_USES_KNOWN_SHORTENER_DOMAIN",
            category=FINDING_CATEGORY_URL,
            severity=FINDING_SEVERITY_MEDIUM,
        ),
    ]
