from application.models.extracted_email import ExtractedEmailContent
from application.use_cases.analyze_extracted_email_text_indicators import (
    AnalyzeExtractedEmailTextIndicatorsCommand,
    AnalyzeExtractedEmailTextIndicatorsUseCase,
)


def test_should_analyze_clean_extracted_email_text_without_findings() -> None:
    use_case = AnalyzeExtractedEmailTextIndicatorsUseCase()
    extracted_email = _extracted_email(
        subject="Monthly report",
        body_text="Your report is ready.",
    )

    result = use_case.execute(
        AnalyzeExtractedEmailTextIndicatorsCommand(
            extracted_email=extracted_email,
            urgency_terms={"urgent"},
            financial_pressure_terms={"payment required"},
            credential_request_terms={"verify your account"},
        )
    )

    assert result.analyzed_text == "Monthly report\nYour report is ready."
    assert result.social_engineering_analysis.findings == []
    assert result.finding_codes == ()


def test_should_include_subject_urgency_finding() -> None:
    use_case = AnalyzeExtractedEmailTextIndicatorsUseCase()
    extracted_email = _extracted_email(
        subject="Urgent account notice",
        body_text="Please review this message.",
    )

    result = use_case.execute(
        AnalyzeExtractedEmailTextIndicatorsCommand(
            extracted_email=extracted_email,
            urgency_terms={"urgent"},
            financial_pressure_terms={"payment required"},
            credential_request_terms={"verify your account"},
        )
    )

    assert result.finding_codes == ("SOCIAL_ENGINEERING_HAS_URGENCY_TERMS",)


def test_should_include_body_financial_pressure_finding() -> None:
    use_case = AnalyzeExtractedEmailTextIndicatorsUseCase()
    extracted_email = _extracted_email(
        subject="Invoice notice",
        body_text="Payment required before the end of the day.",
    )

    result = use_case.execute(
        AnalyzeExtractedEmailTextIndicatorsCommand(
            extracted_email=extracted_email,
            urgency_terms={"urgent"},
            financial_pressure_terms={"payment required"},
            credential_request_terms={"verify your account"},
        )
    )

    assert result.finding_codes == (
        "SOCIAL_ENGINEERING_HAS_FINANCIAL_PRESSURE_TERMS",
    )


def test_should_include_body_credential_request_finding() -> None:
    use_case = AnalyzeExtractedEmailTextIndicatorsUseCase()
    extracted_email = _extracted_email(
        subject="Account notice",
        body_text="Please verify your account to continue.",
    )

    result = use_case.execute(
        AnalyzeExtractedEmailTextIndicatorsCommand(
            extracted_email=extracted_email,
            urgency_terms={"urgent"},
            financial_pressure_terms={"payment required"},
            credential_request_terms={"verify your account"},
        )
    )

    assert result.finding_codes == (
        "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS",
    )


def test_should_include_subject_and_body_findings_in_order() -> None:
    use_case = AnalyzeExtractedEmailTextIndicatorsUseCase()
    extracted_email = _extracted_email(
        subject="Urgent invoice notice",
        body_text="Payment required. Verify your account.",
    )

    result = use_case.execute(
        AnalyzeExtractedEmailTextIndicatorsCommand(
            extracted_email=extracted_email,
            urgency_terms={"urgent"},
            financial_pressure_terms={"payment required"},
            credential_request_terms={"verify your account"},
        )
    )

    assert result.finding_codes == (
        "SOCIAL_ENGINEERING_HAS_URGENCY_TERMS",
        "SOCIAL_ENGINEERING_HAS_FINANCIAL_PRESSURE_TERMS",
        "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS",
    )
    assert result.social_engineering_analysis.risk_level == "CRITICAL"


def test_should_handle_empty_subject_and_body_text() -> None:
    use_case = AnalyzeExtractedEmailTextIndicatorsUseCase()
    extracted_email = _extracted_email(subject="", body_text="")

    result = use_case.execute(
        AnalyzeExtractedEmailTextIndicatorsCommand(
            extracted_email=extracted_email,
            urgency_terms={"urgent"},
            financial_pressure_terms={"payment required"},
            credential_request_terms={"verify your account"},
        )
    )

    assert result.analyzed_text == ""
    assert result.finding_codes == ()


def _extracted_email(subject: str, body_text: str) -> ExtractedEmailContent:
    return ExtractedEmailContent(
        sender_domain="example.com",
        urls=(),
        attachment_filenames=(),
        subject=subject,
        body_text=body_text,
        spf_result="pass",
        dkim_result="none",
        dmarc_result="pass",
    )
