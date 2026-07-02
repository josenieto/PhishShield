import pytest

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


@pytest.mark.parametrize(
    ("code", "severity"),
    [
        ("AUTHENTICATION_DMARC_FAILED", FINDING_SEVERITY_CRITICAL),
        ("AUTHENTICATION_SPF_FAILED", FINDING_SEVERITY_HIGH),
        ("AUTHENTICATION_DKIM_FAILED", FINDING_SEVERITY_HIGH),
        ("AUTHENTICATION_HAS_MULTIPLE_FAILURES", FINDING_SEVERITY_CRITICAL),
        ("AUTHENTICATION_RESULTS_UNKNOWN", FINDING_SEVERITY_MEDIUM),
    ],
)
def test_should_build_authentication_finding_from_code(
    code: str,
    severity: str,
) -> None:
    assert build_finding_from_code(code) == Finding(
        code=code,
        category=FINDING_CATEGORY_AUTHENTICATION,
        severity=severity,
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
