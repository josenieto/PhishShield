from application.models.extracted_email import ExtractedEmailContent
from application.use_cases.analyze_extracted_email_technical_indicators import (
    AnalyzeExtractedEmailTechnicalIndicatorsCommand,
    AnalyzeExtractedEmailTechnicalIndicatorsUseCase,
)


def test_should_analyze_clean_extracted_email_without_findings() -> None:
    use_case = AnalyzeExtractedEmailTechnicalIndicatorsUseCase()
    extracted_email = ExtractedEmailContent(
        sender_domain="example.com",
        urls=("https://example.com/login",),
        attachment_filenames=("invoice.pdf",),
        subject="Invoice available",
        body_text="Please review the attached invoice.",
        spf_result="pass",
        dkim_result="none",
        dmarc_result="pass",
    )

    result = use_case.execute(
        AnalyzeExtractedEmailTechnicalIndicatorsCommand(
            extracted_email=extracted_email,
            suspicious_tlds={"zip"},
            allowed_url_schemes={"https"},
            known_shorteners={"bit.ly"},
        )
    )

    assert result.domain_analysis.findings == []
    assert len(result.url_analyses) == 1
    assert result.url_analyses[0].findings == []
    assert len(result.attachment_analyses) == 1
    assert result.attachment_analyses[0].findings == []
    assert result.authentication_analysis.findings == []
    assert result.finding_codes == ()


def test_should_include_sender_domain_findings() -> None:
    use_case = AnalyzeExtractedEmailTechnicalIndicatorsUseCase()
    extracted_email = ExtractedEmailContent(
        sender_domain="xn--paypl-3ve.zip",
        urls=(),
        attachment_filenames=(),
        subject="",
        body_text="",
        spf_result="pass",
        dkim_result="none",
        dmarc_result="pass",
    )

    result = use_case.execute(
        AnalyzeExtractedEmailTechnicalIndicatorsCommand(
            extracted_email=extracted_email,
            suspicious_tlds={"zip"},
            allowed_url_schemes={"https"},
            known_shorteners=set(),
        )
    )

    assert result.domain_analysis.findings == [
        "DOMAIN_CONTAINS_PUNYCODE",
        "DOMAIN_HAS_SUSPICIOUS_TLD",
    ]
    assert result.finding_codes == (
        "DOMAIN_CONTAINS_PUNYCODE",
        "DOMAIN_HAS_SUSPICIOUS_TLD",
    )


def test_should_include_url_findings_in_input_order() -> None:
    use_case = AnalyzeExtractedEmailTechnicalIndicatorsUseCase()
    extracted_email = ExtractedEmailContent(
        sender_domain="example.com",
        urls=(
            "https://user:pass@example.com/login",
            "https://bit.ly/reset",
        ),
        attachment_filenames=(),
        subject="",
        body_text="",
        spf_result="pass",
        dkim_result="none",
        dmarc_result="pass",
    )

    result = use_case.execute(
        AnalyzeExtractedEmailTechnicalIndicatorsCommand(
            extracted_email=extracted_email,
            suspicious_tlds={"zip"},
            allowed_url_schemes={"https"},
            known_shorteners={"bit.ly"},
        )
    )

    assert [analysis.url for analysis in result.url_analyses] == [
        "https://user:pass@example.com/login",
        "https://bit.ly/reset",
    ]
    assert result.finding_codes == (
        "URL_HAS_EMBEDDED_CREDENTIALS",
        "URL_USES_KNOWN_SHORTENER_DOMAIN",
    )


def test_should_include_attachment_findings_in_input_order() -> None:
    use_case = AnalyzeExtractedEmailTechnicalIndicatorsUseCase()
    extracted_email = ExtractedEmailContent(
        sender_domain="example.com",
        urls=(),
        attachment_filenames=(
            "payload.exe",
            "invoice.pdf.exe",
        ),
        subject="",
        body_text="",
        spf_result="pass",
        dkim_result="none",
        dmarc_result="pass",
    )

    result = use_case.execute(
        AnalyzeExtractedEmailTechnicalIndicatorsCommand(
            extracted_email=extracted_email,
            suspicious_tlds={"zip"},
            allowed_url_schemes={"https"},
            known_shorteners=set(),
        )
    )

    assert [analysis.filename for analysis in result.attachment_analyses] == [
        "payload.exe",
        "invoice.pdf.exe",
    ]
    assert result.finding_codes == (
        "ATTACHMENT_HAS_EXECUTABLE_EXTENSION",
        "ATTACHMENT_HAS_EXECUTABLE_EXTENSION",
        "ATTACHMENT_HAS_DOUBLE_EXTENSION",
    )


def test_should_include_authentication_findings() -> None:
    use_case = AnalyzeExtractedEmailTechnicalIndicatorsUseCase()
    extracted_email = ExtractedEmailContent(
        sender_domain="example.com",
        urls=(),
        attachment_filenames=(),
        subject="",
        body_text="",
        spf_result="fail",
        dkim_result="softfail",
        dmarc_result="pass",
    )

    result = use_case.execute(
        AnalyzeExtractedEmailTechnicalIndicatorsCommand(
            extracted_email=extracted_email,
            suspicious_tlds={"zip"},
            allowed_url_schemes={"https"},
            known_shorteners=set(),
        )
    )

    assert result.authentication_analysis.findings == [
        "AUTHENTICATION_SPF_FAILED",
        "AUTHENTICATION_DKIM_FAILED",
        "AUTHENTICATION_HAS_MULTIPLE_FAILURES",
    ]
    assert result.finding_codes == (
        "AUTHENTICATION_SPF_FAILED",
        "AUTHENTICATION_DKIM_FAILED",
        "AUTHENTICATION_HAS_MULTIPLE_FAILURES",
    )


def test_should_flatten_technical_findings_in_stable_module_order() -> None:
    use_case = AnalyzeExtractedEmailTechnicalIndicatorsUseCase()
    extracted_email = ExtractedEmailContent(
        sender_domain="xn--paypl-3ve.zip",
        urls=("https://user:pass@example.com/login",),
        attachment_filenames=("payload.exe",),
        subject="",
        body_text="",
        spf_result="fail",
        dkim_result="none",
        dmarc_result="fail",
    )

    result = use_case.execute(
        AnalyzeExtractedEmailTechnicalIndicatorsCommand(
            extracted_email=extracted_email,
            suspicious_tlds={"zip"},
            allowed_url_schemes={"https"},
            known_shorteners=set(),
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
    )


def test_should_handle_empty_urls_and_attachments() -> None:
    use_case = AnalyzeExtractedEmailTechnicalIndicatorsUseCase()
    extracted_email = ExtractedEmailContent(
        sender_domain="example.com",
        urls=(),
        attachment_filenames=(),
        subject="",
        body_text="",
        spf_result="pass",
        dkim_result="none",
        dmarc_result="pass",
    )

    result = use_case.execute(
        AnalyzeExtractedEmailTechnicalIndicatorsCommand(
            extracted_email=extracted_email,
            suspicious_tlds={"zip"},
            allowed_url_schemes={"https"},
            known_shorteners=set(),
        )
    )

    assert result.url_analyses == ()
    assert result.attachment_analyses == ()
    assert result.finding_codes == ()
