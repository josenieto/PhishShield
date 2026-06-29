from application.use_cases.summarize_analysis_findings import (
    SummarizeAnalysisFindingsCommand,
    SummarizeAnalysisFindingsUseCase,
)
from domain.value_objects.finding import (
    FINDING_CATEGORY_AUTHENTICATION,
    FINDING_CATEGORY_DOMAIN,
    FINDING_CATEGORY_URL,
    FINDING_SEVERITY_CRITICAL,
    FINDING_SEVERITY_HIGH,
    FINDING_SEVERITY_LOW,
    Finding,
)


def test_should_summarize_empty_findings() -> None:
    use_case = SummarizeAnalysisFindingsUseCase()

    result = use_case.execute(SummarizeAnalysisFindingsCommand(findings=[]))

    assert result.findings == []
    assert result.sorted_findings == []
    assert result.finding_counts_by_category == {}
    assert result.highest_severity == "UNKNOWN"
    assert result.total_findings == 0


def test_should_summarize_total_findings() -> None:
    use_case = SummarizeAnalysisFindingsUseCase()
    findings = [
        Finding("DOMAIN_CONTAINS_PUNYCODE", FINDING_CATEGORY_DOMAIN, FINDING_SEVERITY_HIGH),
        Finding("URL_HAS_EMBEDDED_CREDENTIALS", FINDING_CATEGORY_URL, FINDING_SEVERITY_HIGH),
    ]

    result = use_case.execute(SummarizeAnalysisFindingsCommand(findings=findings))

    assert result.total_findings == 2


def test_should_sort_findings_by_severity() -> None:
    use_case = SummarizeAnalysisFindingsUseCase()
    low_finding = Finding("LOW_FINDING", FINDING_CATEGORY_URL, FINDING_SEVERITY_LOW)
    critical_finding = Finding(
        "CRITICAL_FINDING",
        FINDING_CATEGORY_AUTHENTICATION,
        FINDING_SEVERITY_CRITICAL,
    )
    high_finding = Finding("HIGH_FINDING", FINDING_CATEGORY_DOMAIN, FINDING_SEVERITY_HIGH)

    result = use_case.execute(
        SummarizeAnalysisFindingsCommand(
            findings=[low_finding, critical_finding, high_finding]
        )
    )

    assert result.sorted_findings == [
        critical_finding,
        high_finding,
        low_finding,
    ]


def test_should_count_findings_by_category() -> None:
    use_case = SummarizeAnalysisFindingsUseCase()
    findings = [
        Finding("DOMAIN_CONTAINS_PUNYCODE", FINDING_CATEGORY_DOMAIN, FINDING_SEVERITY_HIGH),
        Finding("DOMAIN_HAS_MIXED_SCRIPTS", FINDING_CATEGORY_DOMAIN, FINDING_SEVERITY_LOW),
        Finding("URL_HAS_EMBEDDED_CREDENTIALS", FINDING_CATEGORY_URL, FINDING_SEVERITY_HIGH),
    ]

    result = use_case.execute(SummarizeAnalysisFindingsCommand(findings=findings))

    assert result.finding_counts_by_category == {
        FINDING_CATEGORY_DOMAIN: 2,
        FINDING_CATEGORY_URL: 1,
    }


def test_should_return_highest_severity() -> None:
    use_case = SummarizeAnalysisFindingsUseCase()
    findings = [
        Finding("DOMAIN_CONTAINS_PUNYCODE", FINDING_CATEGORY_DOMAIN, FINDING_SEVERITY_HIGH),
        Finding(
            "AUTHENTICATION_DMARC_FAILED",
            FINDING_CATEGORY_AUTHENTICATION,
            FINDING_SEVERITY_CRITICAL,
        ),
    ]

    result = use_case.execute(SummarizeAnalysisFindingsCommand(findings=findings))

    assert result.highest_severity == FINDING_SEVERITY_CRITICAL


def test_should_preserve_original_findings_order() -> None:
    use_case = SummarizeAnalysisFindingsUseCase()
    low_finding = Finding("LOW_FINDING", FINDING_CATEGORY_URL, FINDING_SEVERITY_LOW)
    high_finding = Finding("HIGH_FINDING", FINDING_CATEGORY_DOMAIN, FINDING_SEVERITY_HIGH)
    findings = [low_finding, high_finding]

    result = use_case.execute(SummarizeAnalysisFindingsCommand(findings=findings))

    assert result.findings == [low_finding, high_finding]
