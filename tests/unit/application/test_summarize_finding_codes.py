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

    assert result.findings == [
        Finding(
            "DOMAIN_CONTAINS_PUNYCODE",
            FINDING_CATEGORY_DOMAIN,
            FINDING_SEVERITY_HIGH,
        ),
        Finding(
            "URL_HAS_EMBEDDED_CREDENTIALS",
            FINDING_CATEGORY_URL,
            FINDING_SEVERITY_HIGH,
        ),
    ]
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

    assert result.findings == [
        Finding(
            "UNKNOWN_CODE",
            FINDING_CATEGORY_UNKNOWN,
            FINDING_SEVERITY_UNKNOWN,
        )
    ]
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

    assert result.sorted_findings == [
        Finding(
            "AUTHENTICATION_DMARC_FAILED",
            FINDING_CATEGORY_AUTHENTICATION,
            FINDING_SEVERITY_CRITICAL,
        ),
        Finding(
            "UNKNOWN_CODE",
            FINDING_CATEGORY_UNKNOWN,
            FINDING_SEVERITY_UNKNOWN,
        ),
    ]
