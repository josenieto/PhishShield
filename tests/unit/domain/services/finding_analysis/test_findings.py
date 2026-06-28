from domain.services.finding_analysis.findings import (
    deduplicate_finding_codes,
    filter_findings_by_category,
)
from domain.value_objects.finding import (
    FINDING_CATEGORY_AUTHENTICATION,
    FINDING_CATEGORY_DOMAIN,
    FINDING_CATEGORY_URL,
    FINDING_SEVERITY_HIGH,
    FINDING_SEVERITY_MEDIUM,
    Finding,
)


def test_should_remove_duplicate_finding_codes_preserving_order() -> None:
    finding_codes = [
        "URL_HAS_EMBEDDED_CREDENTIALS",
        "DOMAIN_CONTAINS_PUNYCODE",
        "URL_HAS_EMBEDDED_CREDENTIALS",
    ]

    assert deduplicate_finding_codes(finding_codes) == [
        "URL_HAS_EMBEDDED_CREDENTIALS",
        "DOMAIN_CONTAINS_PUNYCODE",
    ]


def test_should_keep_finding_codes_without_duplicates() -> None:
    finding_codes = [
        "DOMAIN_CONTAINS_PUNYCODE",
        "URL_HAS_EMBEDDED_CREDENTIALS",
        "ATTACHMENT_HAS_DOUBLE_EXTENSION",
    ]

    assert deduplicate_finding_codes(finding_codes) == finding_codes


def test_should_return_empty_list_when_finding_codes_are_empty() -> None:
    assert deduplicate_finding_codes([]) == []


def test_should_preserve_first_finding_code_occurrence_order() -> None:
    finding_codes = [
        "B_FINDING",
        "A_FINDING",
        "B_FINDING",
        "C_FINDING",
        "A_FINDING",
    ]

    assert deduplicate_finding_codes(finding_codes) == [
        "B_FINDING",
        "A_FINDING",
        "C_FINDING",
    ]


def test_should_keep_case_sensitive_finding_codes_distinct() -> None:
    assert deduplicate_finding_codes(["A_FINDING", "a_finding"]) == [
        "A_FINDING",
        "a_finding",
    ]


def test_should_keep_empty_finding_code_once() -> None:
    assert deduplicate_finding_codes(["", "", "A_FINDING"]) == [
        "",
        "A_FINDING",
    ]


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
