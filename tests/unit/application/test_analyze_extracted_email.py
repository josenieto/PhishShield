from application.models.extracted_email import ExtractedEmailContent
from application.use_cases.analyze_extracted_email import (
    AnalyzeExtractedEmailCommand,
    AnalyzeExtractedEmailUseCase,
)


def test_should_analyze_clean_extracted_email() -> None:
    use_case = AnalyzeExtractedEmailUseCase()
    extracted_email = _extracted_email(
        sender_domain="example.com",
        urls=("https://example.com/login",),
        attachment_filenames=("invoice.pdf",),
        subject="Monthly report",
        body_text="Your report is ready.",
        spf_result="pass",
        dkim_result="none",
        dmarc_result="pass",
    )

    result = use_case.execute(
        AnalyzeExtractedEmailCommand(
            extracted_email=extracted_email,
            suspicious_tlds={"zip"},
            allowed_url_schemes={"https"},
            known_shorteners={"bit.ly"},
            urgency_terms={"urgent"},
            financial_pressure_terms={"payment required"},
            credential_request_terms={"verify your account"},
            finding_weights={},
            critical_indicators=set(),
        )
    )

    assert result.technical_analysis.finding_codes == ()
    assert result.text_analysis.finding_codes == ()
    assert result.extracted_email == extracted_email
    assert result.finding_codes == ()
    assert result.unique_finding_codes == ()
    assert result.finding_code_summary.total_findings == 0
    assert result.risk_score.raw_score == 0
    assert result.risk_score.risk_level == "LOW"


def test_should_combine_technical_and_text_findings() -> None:
    use_case = AnalyzeExtractedEmailUseCase()
    extracted_email = _extracted_email(
        sender_domain="xn--paypl-3ve.zip",
        urls=("https://user:pass@example.com/login",),
        attachment_filenames=("payload.exe",),
        subject="Urgent account notice",
        body_text="Please verify your account to continue.",
        spf_result="fail",
        dkim_result="none",
        dmarc_result="fail",
    )

    result = use_case.execute(
        AnalyzeExtractedEmailCommand(
            extracted_email=extracted_email,
            suspicious_tlds={"zip"},
            allowed_url_schemes={"https"},
            known_shorteners=set(),
            urgency_terms={"urgent"},
            financial_pressure_terms={"payment required"},
            credential_request_terms={"verify your account"},
            finding_weights={},
            critical_indicators=set(),
        )
    )

    assert result.finding_codes == (
        "DOMAIN_CONTAINS_PUNYCODE",
        "DOMAIN_HAS_SUSPICIOUS_TLD",
        "URL_HAS_EMBEDDED_CREDENTIALS",
        "ATTACHMENT_HAS_EXECUTABLE_EXTENSION",
        "AUTHENTICATION_SPF_FAILED",
        "AUTHENTICATION_DMARC_FAILED",
        "AUTHENTICATION_HAS_MULTIPLE_FAILURES",
        "SOCIAL_ENGINEERING_HAS_URGENCY_TERMS",
        "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS",
    )
    assert result.finding_code_summary.highest_severity == "CRITICAL"


def test_should_deduplicate_findings_for_summary_and_risk_score() -> None:
    use_case = AnalyzeExtractedEmailUseCase()
    extracted_email = _extracted_email(
        sender_domain="example.com",
        urls=(),
        attachment_filenames=("payload.exe", "dropper.exe"),
        subject="",
        body_text="",
        spf_result="pass",
        dkim_result="none",
        dmarc_result="pass",
    )

    result = use_case.execute(
        AnalyzeExtractedEmailCommand(
            extracted_email=extracted_email,
            suspicious_tlds={"zip"},
            allowed_url_schemes={"https"},
            known_shorteners=set(),
            urgency_terms={"urgent"},
            financial_pressure_terms={"payment required"},
            credential_request_terms={"verify your account"},
            finding_weights={"ATTACHMENT_HAS_EXECUTABLE_EXTENSION": 40},
            critical_indicators={"ATTACHMENT_HAS_EXECUTABLE_EXTENSION"},
        )
    )

    assert result.finding_codes == (
        "ATTACHMENT_HAS_EXECUTABLE_EXTENSION",
        "ATTACHMENT_HAS_EXECUTABLE_EXTENSION",
    )
    assert result.unique_finding_codes == ("ATTACHMENT_HAS_EXECUTABLE_EXTENSION",)
    assert result.finding_code_summary.total_findings == 1
    assert result.risk_score.raw_score == 40
    assert result.risk_score.has_critical_indicators is True


def test_should_calculate_risk_score_from_unique_findings() -> None:
    use_case = AnalyzeExtractedEmailUseCase()
    extracted_email = _extracted_email(
        sender_domain="xn--paypl-3ve.zip",
        urls=("https://user:pass@example.com/login",),
        attachment_filenames=(),
        subject="",
        body_text="",
        spf_result="pass",
        dkim_result="none",
        dmarc_result="pass",
    )

    result = use_case.execute(
        AnalyzeExtractedEmailCommand(
            extracted_email=extracted_email,
            suspicious_tlds={"zip"},
            allowed_url_schemes={"https"},
            known_shorteners=set(),
            urgency_terms={"urgent"},
            financial_pressure_terms={"payment required"},
            credential_request_terms={"verify your account"},
            finding_weights={
                "DOMAIN_CONTAINS_PUNYCODE": 30,
                "DOMAIN_HAS_SUSPICIOUS_TLD": 20,
                "URL_HAS_EMBEDDED_CREDENTIALS": 25,
            },
            critical_indicators=set(),
        )
    )

    assert result.risk_score.raw_score == 75
    assert result.risk_score.capped_score == 75
    assert result.risk_score.risk_level == "CRITICAL"


def test_should_preserve_module_analysis_results() -> None:
    use_case = AnalyzeExtractedEmailUseCase()
    extracted_email = _extracted_email(
        sender_domain="example.com",
        urls=("https://bit.ly/reset",),
        attachment_filenames=("invoice.pdf.exe",),
        subject="Urgent notice",
        body_text="Payment required.",
        spf_result="fail",
        dkim_result="softfail",
        dmarc_result="pass",
    )

    result = use_case.execute(
        AnalyzeExtractedEmailCommand(
            extracted_email=extracted_email,
            suspicious_tlds={"zip"},
            allowed_url_schemes={"https"},
            known_shorteners={"bit.ly"},
            urgency_terms={"urgent"},
            financial_pressure_terms={"payment required"},
            credential_request_terms={"verify your account"},
            finding_weights={},
            critical_indicators=set(),
        )
    )

    assert result.technical_analysis.url_analyses[0].domain == "bit.ly"
    assert result.technical_analysis.attachment_analyses[0].filename == "invoice.pdf.exe"
    assert result.technical_analysis.authentication_analysis.has_failure is True
    assert result.text_analysis.analyzed_text == "Urgent notice\nPayment required."


def _extracted_email(
    sender_domain: str,
    urls: tuple[str, ...],
    attachment_filenames: tuple[str, ...],
    subject: str,
    body_text: str,
    spf_result: str,
    dkim_result: str,
    dmarc_result: str,
) -> ExtractedEmailContent:
    return ExtractedEmailContent(
        sender_domain=sender_domain,
        urls=urls,
        attachment_filenames=attachment_filenames,
        subject=subject,
        body_text=body_text,
        spf_result=spf_result,
        dkim_result=dkim_result,
        dmarc_result=dmarc_result,
    )
