from domain.services.finding_analysis.findings import deduplicate_finding_codes


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
