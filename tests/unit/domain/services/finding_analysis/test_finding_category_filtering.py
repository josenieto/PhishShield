from domain.services.finding_analysis.findings import filter_findings_by_category
from domain.value_objects.finding import (
    FINDING_CATEGORY_AUTHENTICATION,
    FINDING_CATEGORY_DOMAIN,
    FINDING_CATEGORY_URL,
    FINDING_SEVERITY_HIGH,
    FINDING_SEVERITY_MEDIUM,
    Finding,
)


def test_should_filter_findings_by_existing_category() -> None:
    findings = [
        Finding("DOMAIN_CONTAINS_PUNYCODE", FINDING_CATEGORY_DOMAIN, FINDING_SEVERITY_HIGH),
        Finding("URL_HAS_EMBEDDED_CREDENTIALS", FINDING_CATEGORY_URL, FINDING_SEVERITY_HIGH),
    ]

    assert filter_findings_by_category(findings, FINDING_CATEGORY_URL) == [
        Finding("URL_HAS_EMBEDDED_CREDENTIALS", FINDING_CATEGORY_URL, FINDING_SEVERITY_HIGH),
    ]


def test_should_return_empty_list_when_finding_category_is_missing() -> None:
    findings = [
        Finding("DOMAIN_CONTAINS_PUNYCODE", FINDING_CATEGORY_DOMAIN, FINDING_SEVERITY_HIGH),
    ]

    assert filter_findings_by_category(findings, FINDING_CATEGORY_URL) == []


def test_should_preserve_order_when_filtering_findings_by_category() -> None:
    first_url_finding = Finding(
        "URL_HAS_EMBEDDED_CREDENTIALS",
        FINDING_CATEGORY_URL,
        FINDING_SEVERITY_HIGH,
    )
    second_url_finding = Finding(
        "URL_USES_KNOWN_SHORTENER_DOMAIN",
        FINDING_CATEGORY_URL,
        FINDING_SEVERITY_MEDIUM,
    )
    findings = [
        first_url_finding,
        Finding("DOMAIN_CONTAINS_PUNYCODE", FINDING_CATEGORY_DOMAIN, FINDING_SEVERITY_HIGH),
        second_url_finding,
    ]

    assert filter_findings_by_category(findings, FINDING_CATEGORY_URL) == [
        first_url_finding,
        second_url_finding,
    ]


def test_should_filter_findings_by_category_case_sensitively() -> None:
    findings = [
        Finding("URL_HAS_EMBEDDED_CREDENTIALS", "url", FINDING_SEVERITY_HIGH),
        Finding("URL_USES_KNOWN_SHORTENER_DOMAIN", FINDING_CATEGORY_URL, FINDING_SEVERITY_MEDIUM),
    ]

    assert filter_findings_by_category(findings, FINDING_CATEGORY_URL) == [
        Finding("URL_USES_KNOWN_SHORTENER_DOMAIN", FINDING_CATEGORY_URL, FINDING_SEVERITY_MEDIUM),
    ]


def test_should_return_empty_list_when_filtering_empty_findings() -> None:
    assert filter_findings_by_category([], FINDING_CATEGORY_AUTHENTICATION) == []
