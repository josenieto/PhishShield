from domain.services.finding_analysis.findings import get_highest_finding_severity
from domain.value_objects.finding import (
    FINDING_CATEGORY_ATTACHMENT,
    FINDING_CATEGORY_AUTHENTICATION,
    FINDING_CATEGORY_DOMAIN,
    FINDING_CATEGORY_UNKNOWN,
    FINDING_CATEGORY_URL,
    FINDING_SEVERITY_CRITICAL,
    FINDING_SEVERITY_HIGH,
    FINDING_SEVERITY_LOW,
    FINDING_SEVERITY_MEDIUM,
    FINDING_SEVERITY_UNKNOWN,
    Finding,
)


def test_should_return_unknown_as_highest_severity_when_findings_are_empty() -> None:
    assert get_highest_finding_severity([]) == FINDING_SEVERITY_UNKNOWN


def test_should_get_highest_finding_severity() -> None:
    findings = [
        Finding("LOW_FINDING", FINDING_CATEGORY_URL, FINDING_SEVERITY_LOW),
        Finding("HIGH_FINDING", FINDING_CATEGORY_DOMAIN, FINDING_SEVERITY_HIGH),
        Finding("MEDIUM_FINDING", FINDING_CATEGORY_ATTACHMENT, FINDING_SEVERITY_MEDIUM),
    ]

    assert get_highest_finding_severity(findings) == FINDING_SEVERITY_HIGH


def test_should_return_critical_as_highest_finding_severity() -> None:
    findings = [
        Finding("HIGH_FINDING", FINDING_CATEGORY_URL, FINDING_SEVERITY_HIGH),
        Finding(
            "CRITICAL_FINDING",
            FINDING_CATEGORY_AUTHENTICATION,
            FINDING_SEVERITY_CRITICAL,
        ),
    ]

    assert get_highest_finding_severity(findings) == FINDING_SEVERITY_CRITICAL


def test_should_return_unknown_when_only_unknown_severities_exist() -> None:
    findings = [
        Finding("UNKNOWN_FINDING", FINDING_CATEGORY_UNKNOWN, FINDING_SEVERITY_UNKNOWN),
    ]

    assert get_highest_finding_severity(findings) == FINDING_SEVERITY_UNKNOWN


def test_should_return_unknown_when_only_unrecognized_severities_exist() -> None:
    findings = [
        Finding("CUSTOM_FINDING", FINDING_CATEGORY_UNKNOWN, "CUSTOM"),
    ]

    assert get_highest_finding_severity(findings) == FINDING_SEVERITY_UNKNOWN


def test_should_return_recognized_highest_severity_over_unrecognized_severity() -> None:
    findings = [
        Finding("CUSTOM_FINDING", FINDING_CATEGORY_UNKNOWN, "CUSTOM"),
        Finding("MEDIUM_FINDING", FINDING_CATEGORY_DOMAIN, FINDING_SEVERITY_MEDIUM),
    ]

    assert get_highest_finding_severity(findings) == FINDING_SEVERITY_MEDIUM


def test_should_not_mutate_original_findings_when_getting_highest_severity() -> None:
    low_finding = Finding("LOW_FINDING", FINDING_CATEGORY_URL, FINDING_SEVERITY_LOW)
    high_finding = Finding("HIGH_FINDING", FINDING_CATEGORY_DOMAIN, FINDING_SEVERITY_HIGH)
    findings = [low_finding, high_finding]

    assert get_highest_finding_severity(findings) == FINDING_SEVERITY_HIGH
    assert findings == [low_finding, high_finding]
