from application.use_cases.analyze_social_engineering_indicators import (
    AnalyzeSocialEngineeringIndicatorsCommand,
    AnalyzeSocialEngineeringIndicatorsUseCase,
)


def test_should_analyze_clean_text_without_findings() -> None:
    use_case = AnalyzeSocialEngineeringIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeSocialEngineeringIndicatorsCommand(
            text="Your monthly report is ready.",
            urgency_terms={"urgent"},
            financial_pressure_terms={"payment required"},
            credential_request_terms={"verify your account"},
        )
    )

    assert result.text == "Your monthly report is ready."
    assert result.has_urgency_terms is False
    assert result.has_financial_pressure_terms is False
    assert result.has_credential_request_terms is False
    assert result.signal_counts == {
        "urgency": 0,
        "financial_pressure": 0,
        "credential_request": 0,
    }
    assert result.risk_level == "LOW"
    assert result.findings == []


def test_should_report_urgency_finding() -> None:
    use_case = AnalyzeSocialEngineeringIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeSocialEngineeringIndicatorsCommand(
            text="Act now to avoid account suspension.",
            urgency_terms={"act now"},
            financial_pressure_terms={"payment required"},
            credential_request_terms={"verify your account"},
        )
    )

    assert result.has_urgency_terms is True
    assert result.risk_level == "MEDIUM"
    assert result.findings == ["SOCIAL_ENGINEERING_HAS_URGENCY_TERMS"]


def test_should_report_financial_pressure_finding() -> None:
    use_case = AnalyzeSocialEngineeringIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeSocialEngineeringIndicatorsCommand(
            text="Payment required before your invoice is closed.",
            urgency_terms={"act now"},
            financial_pressure_terms={"payment required"},
            credential_request_terms={"verify your account"},
        )
    )

    assert result.has_financial_pressure_terms is True
    assert result.risk_level == "MEDIUM"
    assert result.findings == [
        "SOCIAL_ENGINEERING_HAS_FINANCIAL_PRESSURE_TERMS"
    ]


def test_should_report_credential_request_finding() -> None:
    use_case = AnalyzeSocialEngineeringIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeSocialEngineeringIndicatorsCommand(
            text="Please verify your account to continue.",
            urgency_terms={"act now"},
            financial_pressure_terms={"payment required"},
            credential_request_terms={"verify your account"},
        )
    )

    assert result.has_credential_request_terms is True
    assert result.risk_level == "MEDIUM"
    assert result.findings == [
        "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS"
    ]


def test_should_report_multiple_social_engineering_findings_in_order() -> None:
    use_case = AnalyzeSocialEngineeringIndicatorsUseCase()

    result = use_case.execute(
        AnalyzeSocialEngineeringIndicatorsCommand(
            text="Urgent payment required. Verify your account.",
            urgency_terms={"urgent"},
            financial_pressure_terms={"payment required"},
            credential_request_terms={"verify your account"},
        )
    )

    assert result.has_urgency_terms is True
    assert result.has_financial_pressure_terms is True
    assert result.has_credential_request_terms is True
    assert result.signal_counts == {
        "urgency": 1,
        "financial_pressure": 1,
        "credential_request": 1,
    }
    assert result.risk_level == "CRITICAL"
    assert result.findings == [
        "SOCIAL_ENGINEERING_HAS_URGENCY_TERMS",
        "SOCIAL_ENGINEERING_HAS_FINANCIAL_PRESSURE_TERMS",
        "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS",
    ]
