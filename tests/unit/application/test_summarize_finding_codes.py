from application.use_cases.summarize_finding_codes import (
    SummarizeFindingCodesCommand,
    SummarizeFindingCodesUseCase,
)
from domain.value_objects.finding import (
    FINDING_CATEGORY_AUTHENTICATION,
    FINDING_CATEGORY_DOMAIN,
    FINDING_CATEGORY_UNKNOWN,
    FINDING_CATEGORY_URL,
    FINDING_SEVERITY_CRITICAL,
    FINDING_SEVERITY_HIGH,
    FINDING_SEVERITY_UNKNOWN,
    Finding,
)


def test_should_summarize_empty_finding_codes() -> None:
    use_case = SummarizeFindingCodesUseCase()

    result = use_case.execute(SummarizeFindingCodesCommand(finding_codes=[]))

    assert result.findings == []
    assert result.sorted_findings == []
    assert result.finding_counts_by_category == {}
    assert result.highest_severity == FINDING_SEVERITY_UNKNOWN
    assert result.total_findings == 0


def test_should_summarize_known_finding_codes() -> None:
    use_case = SummarizeFindingCodesUseCase()

    result = use_case.execute(
        SummarizeFindingCodesCommand(
            finding_codes=[
                "DOMAIN_CONTAINS_PUNYCODE",
                "URL_HAS_EMBEDDED_CREDENTIALS",
            ]
        )
    )

    assert [finding.code for finding in result.findings] == [
        "DOMAIN_CONTAINS_PUNYCODE",
        "URL_HAS_EMBEDDED_CREDENTIALS",
    ]
    assert [finding.category for finding in result.findings] == [
        FINDING_CATEGORY_DOMAIN,
        FINDING_CATEGORY_URL,
    ]
    assert [finding.severity for finding in result.findings] == [
        FINDING_SEVERITY_HIGH,
        FINDING_SEVERITY_HIGH,
    ]
    assert all(finding.explanation != "" for finding in result.findings)
    assert result.finding_counts_by_category == {
        FINDING_CATEGORY_DOMAIN: 1,
        FINDING_CATEGORY_URL: 1,
    }
    assert result.highest_severity == FINDING_SEVERITY_HIGH
    assert result.total_findings == 2


def test_should_summarize_critical_finding_code() -> None:
    use_case = SummarizeFindingCodesUseCase()

    result = use_case.execute(
        SummarizeFindingCodesCommand(
            finding_codes=["AUTHENTICATION_DMARC_FAILED"]
        )
    )

    assert result.highest_severity == FINDING_SEVERITY_CRITICAL
    assert result.finding_counts_by_category == {FINDING_CATEGORY_AUTHENTICATION: 1}


def test_should_summarize_unknown_finding_code() -> None:
    use_case = SummarizeFindingCodesUseCase()

    result = use_case.execute(
        SummarizeFindingCodesCommand(finding_codes=["UNKNOWN_CODE"])
    )

    assert len(result.findings) == 1
    assert result.findings[0].code == "UNKNOWN_CODE"
    assert result.findings[0].category == FINDING_CATEGORY_UNKNOWN
    assert result.findings[0].severity == FINDING_SEVERITY_UNKNOWN
    assert result.findings[0].explanation == "No explanation is available for this finding code yet."
    assert result.finding_counts_by_category == {FINDING_CATEGORY_UNKNOWN: 1}
    assert result.highest_severity == FINDING_SEVERITY_UNKNOWN


def test_should_preserve_duplicate_finding_codes() -> None:
    use_case = SummarizeFindingCodesUseCase()

    result = use_case.execute(
        SummarizeFindingCodesCommand(
            finding_codes=[
                "DOMAIN_CONTAINS_PUNYCODE",
                "DOMAIN_CONTAINS_PUNYCODE",
            ]
        )
    )

    assert result.total_findings == 2
    assert result.finding_counts_by_category == {FINDING_CATEGORY_DOMAIN: 2}


def test_should_sort_built_findings_by_severity() -> None:
    use_case = SummarizeFindingCodesUseCase()

    result = use_case.execute(
        SummarizeFindingCodesCommand(
            finding_codes=[
                "UNKNOWN_CODE",
                "AUTHENTICATION_DMARC_FAILED",
            ]
        )
    )

    assert [finding.code for finding in result.sorted_findings] == [
        "AUTHENTICATION_DMARC_FAILED",
        "UNKNOWN_CODE",
    ]
    assert [finding.category for finding in result.sorted_findings] == [
        FINDING_CATEGORY_AUTHENTICATION,
        FINDING_CATEGORY_UNKNOWN,
    ]
    assert [finding.severity for finding in result.sorted_findings] == [
        FINDING_SEVERITY_CRITICAL,
        FINDING_SEVERITY_UNKNOWN,
    ]
    assert all(finding.explanation != "" for finding in result.sorted_findings)
