from application.models.extracted_email import ExtractedEmailContent
from application.use_cases.analyze_raw_email import (
    AnalyzeRawEmailCommand,
    AnalyzeRawEmailUseCase,
)


class FakeEmailContentExtractor:
    def __init__(self, extracted_email: ExtractedEmailContent) -> None:
        self.extracted_email = extracted_email
        self.received_email_bytes = b""

    def extract(self, email_bytes: bytes) -> ExtractedEmailContent:
        self.received_email_bytes = email_bytes
        return self.extracted_email


def test_should_pass_raw_email_bytes_to_extractor() -> None:
    extractor = FakeEmailContentExtractor(_extracted_email())
    use_case = AnalyzeRawEmailUseCase(email_content_extractor=extractor)

    use_case.execute(_command(email_bytes=b"raw email bytes"))

    assert extractor.received_email_bytes == b"raw email bytes"


def test_should_analyze_extracted_email_content() -> None:
    extractor = FakeEmailContentExtractor(
        _extracted_email(
            sender_domain="xn--paypl-3ve.zip",
            urls=("https://user:pass@example.com/login",),
            attachment_filenames=("payload.exe",),
            subject="Urgent account notice",
            body_text="Please verify your account.",
            spf_result="fail",
            dkim_result="none",
            dmarc_result="fail",
        )
    )
    use_case = AnalyzeRawEmailUseCase(email_content_extractor=extractor)

    result = use_case.execute(
        _command(
            email_bytes=b"raw email bytes",
            finding_weights={
                "DOMAIN_CONTAINS_PUNYCODE": 30,
                "URL_HAS_EMBEDDED_CREDENTIALS": 25,
                "ATTACHMENT_HAS_EXECUTABLE_EXTENSION": 40,
                "AUTHENTICATION_DMARC_FAILED": 50,
                "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS": 25,
            },
            critical_indicators={"AUTHENTICATION_DMARC_FAILED"},
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
    assert result.risk_score.has_critical_indicators is True


def test_should_use_command_configuration_values() -> None:
    extractor = FakeEmailContentExtractor(
        _extracted_email(
            sender_domain="a.b.c.d.example.zip",
            urls=("ftp://example.com/file",),
            attachment_filenames=(),
            subject="",
            body_text="",
            spf_result="pass",
            dkim_result="none",
            dmarc_result="pass",
        )
    )
    use_case = AnalyzeRawEmailUseCase(email_content_extractor=extractor)

    result = use_case.execute(
        _command(
            email_bytes=b"raw email bytes",
            suspicious_tlds={"zip"},
            allowed_url_schemes={"https"},
            max_subdomain_depth=3,
        )
    )

    assert result.finding_codes == (
        "DOMAIN_HAS_SUSPICIOUS_DEPTH",
        "DOMAIN_HAS_SUSPICIOUS_TLD",
        "URL_SCHEME_NOT_ALLOWED",
    )


def _command(
    email_bytes: bytes,
    suspicious_tlds: set[str] | None = None,
    allowed_url_schemes: set[str] | None = None,
    known_shorteners: set[str] | None = None,
    urgency_terms: set[str] | None = None,
    financial_pressure_terms: set[str] | None = None,
    credential_request_terms: set[str] | None = None,
    finding_weights: dict[str, int] | None = None,
    critical_indicators: set[str] | None = None,
    max_subdomain_depth: int = 4,
    query_density_threshold: int = 3,
) -> AnalyzeRawEmailCommand:
    return AnalyzeRawEmailCommand(
        email_bytes=email_bytes,
        suspicious_tlds=suspicious_tlds or {"zip"},
        allowed_url_schemes=allowed_url_schemes or {"https"},
        known_shorteners=known_shorteners or {"bit.ly"},
        urgency_terms=urgency_terms or {"urgent"},
        financial_pressure_terms=financial_pressure_terms or {"payment required"},
        credential_request_terms=credential_request_terms or {"verify your account"},
        finding_weights=finding_weights or {},
        critical_indicators=critical_indicators or set(),
        max_subdomain_depth=max_subdomain_depth,
        query_density_threshold=query_density_threshold,
    )


def _extracted_email(
    sender_domain: str = "example.com",
    urls: tuple[str, ...] = (),
    attachment_filenames: tuple[str, ...] = (),
    subject: str = "",
    body_text: str = "",
    spf_result: str = "pass",
    dkim_result: str = "none",
    dmarc_result: str = "pass",
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
