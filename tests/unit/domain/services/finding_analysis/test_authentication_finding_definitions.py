from domain.services.finding_analysis.finding_definitions import (
    build_finding_from_code,
    build_findings_from_codes,
)
from domain.value_objects.finding import (
    FINDING_CATEGORY_AUTHENTICATION,
    FINDING_SEVERITY_CRITICAL,
    FINDING_SEVERITY_HIGH,
    FINDING_SEVERITY_MEDIUM,
    Finding,
)


def test_should_build_known_authentication_finding_from_code() -> None:
    assert build_finding_from_code("AUTHENTICATION_DMARC_FAILED") == Finding(
        code="AUTHENTICATION_DMARC_FAILED",
        category=FINDING_CATEGORY_AUTHENTICATION,
        severity=FINDING_SEVERITY_CRITICAL,
    )


def test_should_build_spf_failed_authentication_finding_from_code() -> None:
    assert build_finding_from_code("AUTHENTICATION_SPF_FAILED") == Finding(
        code="AUTHENTICATION_SPF_FAILED",
        category=FINDING_CATEGORY_AUTHENTICATION,
        severity=FINDING_SEVERITY_HIGH,
    )


def test_should_build_dkim_failed_authentication_finding_from_code() -> None:
    assert build_finding_from_code("AUTHENTICATION_DKIM_FAILED") == Finding(
        code="AUTHENTICATION_DKIM_FAILED",
        category=FINDING_CATEGORY_AUTHENTICATION,
        severity=FINDING_SEVERITY_HIGH,
    )


def test_should_build_multiple_failures_authentication_finding_from_code() -> None:
    assert build_finding_from_code("AUTHENTICATION_HAS_MULTIPLE_FAILURES") == Finding(
        code="AUTHENTICATION_HAS_MULTIPLE_FAILURES",
        category=FINDING_CATEGORY_AUTHENTICATION,
        severity=FINDING_SEVERITY_CRITICAL,
    )


def test_should_build_unknown_results_authentication_finding_from_code() -> None:
    assert build_finding_from_code("AUTHENTICATION_RESULTS_UNKNOWN") == Finding(
        code="AUTHENTICATION_RESULTS_UNKNOWN",
        category=FINDING_CATEGORY_AUTHENTICATION,
        severity=FINDING_SEVERITY_MEDIUM,
    )


def test_should_build_authentication_findings_from_codes_preserving_order() -> None:
    assert build_findings_from_codes(
        [
            "AUTHENTICATION_SPF_FAILED",
            "AUTHENTICATION_DKIM_FAILED",
            "AUTHENTICATION_DMARC_FAILED",
            "AUTHENTICATION_HAS_MULTIPLE_FAILURES",
            "AUTHENTICATION_RESULTS_UNKNOWN",
        ]
    ) == [
        Finding(
            code="AUTHENTICATION_SPF_FAILED",
            category=FINDING_CATEGORY_AUTHENTICATION,
            severity=FINDING_SEVERITY_HIGH,
        ),
        Finding(
            code="AUTHENTICATION_DKIM_FAILED",
            category=FINDING_CATEGORY_AUTHENTICATION,
            severity=FINDING_SEVERITY_HIGH,
        ),
        Finding(
            code="AUTHENTICATION_DMARC_FAILED",
            category=FINDING_CATEGORY_AUTHENTICATION,
            severity=FINDING_SEVERITY_CRITICAL,
        ),
        Finding(
            code="AUTHENTICATION_HAS_MULTIPLE_FAILURES",
            category=FINDING_CATEGORY_AUTHENTICATION,
            severity=FINDING_SEVERITY_CRITICAL,
        ),
        Finding(
            code="AUTHENTICATION_RESULTS_UNKNOWN",
            category=FINDING_CATEGORY_AUTHENTICATION,
            severity=FINDING_SEVERITY_MEDIUM,
        ),
    ]
