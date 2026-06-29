from domain.services.finding_analysis.findings import sort_findings_by_severity
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


def test_should_sort_findings_by_severity() -> None:
    low_finding = Finding("LOW_FINDING", FINDING_CATEGORY_URL, FINDING_SEVERITY_LOW)
    critical_finding = Finding(
        "CRITICAL_FINDING",
        FINDING_CATEGORY_AUTHENTICATION,
        FINDING_SEVERITY_CRITICAL,
    )
    medium_finding = Finding(
        "MEDIUM_FINDING",
        FINDING_CATEGORY_DOMAIN,
        FINDING_SEVERITY_MEDIUM,
    )
    high_finding = Finding(
        "HIGH_FINDING",
        FINDING_CATEGORY_ATTACHMENT,
        FINDING_SEVERITY_HIGH,
    )

    assert sort_findings_by_severity(
        [low_finding, critical_finding, medium_finding, high_finding]
    ) == [
        critical_finding,
        high_finding,
        medium_finding,
        low_finding,
    ]


def test_should_preserve_order_for_findings_with_same_severity() -> None:
    first_finding = Finding("FIRST_FINDING", FINDING_CATEGORY_URL, FINDING_SEVERITY_HIGH)
    second_finding = Finding("SECOND_FINDING", FINDING_CATEGORY_DOMAIN, FINDING_SEVERITY_HIGH)

    assert sort_findings_by_severity([first_finding, second_finding]) == [
        first_finding,
        second_finding,
    ]


def test_should_sort_unknown_severity_last() -> None:
    unknown_finding = Finding(
        "UNKNOWN_FINDING",
        FINDING_CATEGORY_UNKNOWN,
        FINDING_SEVERITY_UNKNOWN,
    )
    low_finding = Finding("LOW_FINDING", FINDING_CATEGORY_URL, FINDING_SEVERITY_LOW)

    assert sort_findings_by_severity([unknown_finding, low_finding]) == [
        low_finding,
        unknown_finding,
    ]


def test_should_treat_unrecognized_severity_as_unknown_when_sorting() -> None:
    unrecognized_finding = Finding(
        "CUSTOM_FINDING",
        FINDING_CATEGORY_UNKNOWN,
        "CUSTOM",
    )
    medium_finding = Finding(
        "MEDIUM_FINDING",
        FINDING_CATEGORY_DOMAIN,
        FINDING_SEVERITY_MEDIUM,
    )

    assert sort_findings_by_severity([unrecognized_finding, medium_finding]) == [
        medium_finding,
        unrecognized_finding,
    ]


def test_should_return_empty_list_when_sorting_empty_findings() -> None:
    assert sort_findings_by_severity([]) == []


def test_should_not_mutate_original_findings_when_sorting_by_severity() -> None:
    low_finding = Finding("LOW_FINDING", FINDING_CATEGORY_URL, FINDING_SEVERITY_LOW)
    high_finding = Finding("HIGH_FINDING", FINDING_CATEGORY_URL, FINDING_SEVERITY_HIGH)
    findings = [low_finding, high_finding]

    assert sort_findings_by_severity(findings) == [high_finding, low_finding]
    assert findings == [low_finding, high_finding]
