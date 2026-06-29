from domain.services.finding_analysis.findings import count_findings_by_category
from domain.value_objects.finding import (
    FINDING_CATEGORY_DOMAIN,
    FINDING_CATEGORY_UNKNOWN,
    FINDING_CATEGORY_URL,
    FINDING_SEVERITY_HIGH,
    FINDING_SEVERITY_MEDIUM,
    Finding,
)


def test_should_count_findings_by_category() -> None:
    findings = [
        Finding("URL_HAS_EMBEDDED_CREDENTIALS", FINDING_CATEGORY_URL, FINDING_SEVERITY_HIGH),
        Finding("URL_USES_KNOWN_SHORTENER_DOMAIN", FINDING_CATEGORY_URL, FINDING_SEVERITY_MEDIUM),
        Finding("DOMAIN_CONTAINS_PUNYCODE", FINDING_CATEGORY_DOMAIN, FINDING_SEVERITY_HIGH),
    ]

    assert count_findings_by_category(findings) == {
        FINDING_CATEGORY_URL: 2,
        FINDING_CATEGORY_DOMAIN: 1,
    }


def test_should_count_one_finding_category() -> None:
    findings = [
        Finding("URL_HAS_EMBEDDED_CREDENTIALS", FINDING_CATEGORY_URL, FINDING_SEVERITY_HIGH),
    ]

    assert count_findings_by_category(findings) == {FINDING_CATEGORY_URL: 1}


def test_should_return_empty_counts_when_findings_are_empty() -> None:
    assert count_findings_by_category([]) == {}


def test_should_count_finding_categories_case_sensitively() -> None:
    findings = [
        Finding("URL_HAS_EMBEDDED_CREDENTIALS", FINDING_CATEGORY_URL, FINDING_SEVERITY_HIGH),
        Finding("URL_USES_KNOWN_SHORTENER_DOMAIN", "url", FINDING_SEVERITY_MEDIUM),
    ]

    assert count_findings_by_category(findings) == {
        FINDING_CATEGORY_URL: 1,
        "url": 1,
    }


def test_should_count_unknown_finding_category() -> None:
    findings = [
        Finding("UNKNOWN_FINDING", FINDING_CATEGORY_UNKNOWN, FINDING_SEVERITY_MEDIUM),
    ]

    assert count_findings_by_category(findings) == {FINDING_CATEGORY_UNKNOWN: 1}


def test_should_preserve_first_category_insertion_order_when_counting() -> None:
    findings = [
        Finding("DOMAIN_CONTAINS_PUNYCODE", FINDING_CATEGORY_DOMAIN, FINDING_SEVERITY_HIGH),
        Finding("URL_HAS_EMBEDDED_CREDENTIALS", FINDING_CATEGORY_URL, FINDING_SEVERITY_HIGH),
        Finding("DOMAIN_HAS_MIXED_SCRIPTS", FINDING_CATEGORY_DOMAIN, FINDING_SEVERITY_MEDIUM),
    ]

    assert list(count_findings_by_category(findings)) == [
        FINDING_CATEGORY_DOMAIN,
        FINDING_CATEGORY_URL,
    ]
