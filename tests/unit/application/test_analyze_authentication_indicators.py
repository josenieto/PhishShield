from application.use_cases.analyze_authentication_indicators import (
    AnalyzeAuthenticationIndicatorsCommand,
    AnalyzeAuthenticationIndicatorsUseCase,
)


def test_should_analyze_aligned_authentication_without_findings() -> None:
    use_case = AnalyzeAuthenticationIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeAuthenticationIndicatorsCommand(
            spf_result="pass",
            dkim_result="none",
            dmarc_result="pass",
        )
    )

    assert result.spf_result == "pass"
    assert result.dkim_result == "none"
    assert result.dmarc_result == "pass"
    assert result.is_aligned is True
    assert result.has_failure is False
    assert result.risk_level == "LOW"
    assert result.findings == []


def test_should_report_authentication_failure_findings() -> None:
    use_case = AnalyzeAuthenticationIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeAuthenticationIndicatorsCommand(
            spf_result="fail",
            dkim_result="softfail",
            dmarc_result="pass",
        )
    )

    assert result.is_aligned is False
    assert result.has_failure is True
    assert result.risk_level == "MEDIUM"
    assert result.findings == [
        "AUTHENTICATION_SPF_FAILED",
        "AUTHENTICATION_DKIM_FAILED",
        "AUTHENTICATION_HAS_MULTIPLE_FAILURES",
    ]


def test_should_report_critical_dmarc_authentication_failure() -> None:
    use_case = AnalyzeAuthenticationIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeAuthenticationIndicatorsCommand(
            spf_result="fail",
            dkim_result="none",
            dmarc_result="fail",
        )
    )

    assert result.is_aligned is False
    assert result.has_failure is True
    assert result.risk_level == "CRITICAL"
    assert result.findings == [
        "AUTHENTICATION_SPF_FAILED",
        "AUTHENTICATION_DMARC_FAILED",
        "AUTHENTICATION_HAS_MULTIPLE_FAILURES",
    ]


def test_should_report_unknown_authentication_results() -> None:
    use_case = AnalyzeAuthenticationIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeAuthenticationIndicatorsCommand(
            spf_result="",
            dkim_result=" ",
            dmarc_result="unknown-value",
        )
    )

    assert result.is_aligned is False
    assert result.has_failure is False
    assert result.risk_level == "UNKNOWN"
    assert result.findings == ["AUTHENTICATION_RESULTS_UNKNOWN"]
