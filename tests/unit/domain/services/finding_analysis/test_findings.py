from domain.services.finding_analysis.findings import (
    count_findings_by_category,
    deduplicate_finding_codes,
    filter_findings_by_category,
    sort_findings_by_severity,
)
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
