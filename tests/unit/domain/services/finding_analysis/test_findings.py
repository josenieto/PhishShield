from domain.services.finding_analysis.findings import deduplicate_findings


def test_should_remove_duplicate_findings_preserving_order() -> None:
    findings = [
        "URL_HAS_EMBEDDED_CREDENTIALS",
        "DOMAIN_CONTAINS_PUNYCODE",
        "URL_HAS_EMBEDDED_CREDENTIALS",
    ]

    assert deduplicate_findings(findings) == [
        "URL_HAS_EMBEDDED_CREDENTIALS",
        "DOMAIN_CONTAINS_PUNYCODE",
    ]


def test_should_keep_findings_without_duplicates() -> None:
    findings = [
        "DOMAIN_CONTAINS_PUNYCODE",
        "URL_HAS_EMBEDDED_CREDENTIALS",
        "ATTACHMENT_HAS_DOUBLE_EXTENSION",
    ]

    assert deduplicate_findings(findings) == findings


def test_should_return_empty_list_when_findings_are_empty() -> None:
    assert deduplicate_findings([]) == []


def test_should_preserve_first_occurrence_order() -> None:
    findings = [
        "B_FINDING",
        "A_FINDING",
        "B_FINDING",
        "C_FINDING",
        "A_FINDING",
    ]

    assert deduplicate_findings(findings) == [
        "B_FINDING",
        "A_FINDING",
        "C_FINDING",
    ]


def test_should_keep_case_sensitive_findings_distinct() -> None:
    assert deduplicate_findings(["A_FINDING", "a_finding"]) == [
        "A_FINDING",
        "a_finding",
    ]


def test_should_keep_empty_finding_once() -> None:
    assert deduplicate_findings(["", "", "A_FINDING"]) == ["", "A_FINDING"]
