from domain.services.finding_analysis.finding_definitions import (
    build_finding_from_code,
    build_findings_from_codes,
)
from domain.value_objects.finding import (
    FINDING_CATEGORY_SOCIAL_ENGINEERING,
    FINDING_SEVERITY_HIGH,
    FINDING_SEVERITY_MEDIUM,
    Finding,
)


def test_should_build_known_social_engineering_finding_from_code() -> None:
    assert build_finding_from_code(
        "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS"
    ) == Finding(
        code="SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS",
        category=FINDING_CATEGORY_SOCIAL_ENGINEERING,
        severity=FINDING_SEVERITY_HIGH,
    )


def test_should_build_urgency_social_engineering_finding_from_code() -> None:
    assert build_finding_from_code("SOCIAL_ENGINEERING_HAS_URGENCY_TERMS") == Finding(
        code="SOCIAL_ENGINEERING_HAS_URGENCY_TERMS",
        category=FINDING_CATEGORY_SOCIAL_ENGINEERING,
        severity=FINDING_SEVERITY_MEDIUM,
    )


def test_should_build_financial_pressure_social_engineering_finding_from_code() -> None:
    assert build_finding_from_code(
        "SOCIAL_ENGINEERING_HAS_FINANCIAL_PRESSURE_TERMS"
    ) == Finding(
        code="SOCIAL_ENGINEERING_HAS_FINANCIAL_PRESSURE_TERMS",
        category=FINDING_CATEGORY_SOCIAL_ENGINEERING,
        severity=FINDING_SEVERITY_MEDIUM,
    )


def test_should_build_social_engineering_findings_from_codes_preserving_order() -> None:
    assert build_findings_from_codes(
        [
            "SOCIAL_ENGINEERING_HAS_URGENCY_TERMS",
            "SOCIAL_ENGINEERING_HAS_FINANCIAL_PRESSURE_TERMS",
            "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS",
        ]
    ) == [
        Finding(
            code="SOCIAL_ENGINEERING_HAS_URGENCY_TERMS",
            category=FINDING_CATEGORY_SOCIAL_ENGINEERING,
            severity=FINDING_SEVERITY_MEDIUM,
        ),
        Finding(
            code="SOCIAL_ENGINEERING_HAS_FINANCIAL_PRESSURE_TERMS",
            category=FINDING_CATEGORY_SOCIAL_ENGINEERING,
            severity=FINDING_SEVERITY_MEDIUM,
        ),
        Finding(
            code="SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS",
            category=FINDING_CATEGORY_SOCIAL_ENGINEERING,
            severity=FINDING_SEVERITY_HIGH,
        ),
    ]
