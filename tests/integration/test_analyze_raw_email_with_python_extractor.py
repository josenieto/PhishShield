from application.use_cases.analyze_raw_email import (
    AnalyzeRawEmailCommand,
    AnalyzeRawEmailUseCase,
)
from infrastructure.adapters.email_parser.python_email_content_extractor import (
    PythonEmailContentExtractorAdapter,
)


def test_should_analyze_raw_email_with_python_extractor() -> None:
    use_case = AnalyzeRawEmailUseCase(
        email_content_extractor=PythonEmailContentExtractorAdapter()
    )
    email_bytes = b"\r\n".join(
        [
            b"From: Alice <alice@xn--paypl-3ve.zip>",
            b"Subject: Urgent account notice",
            b"Authentication-Results: mx.example.com; spf=fail smtp.mailfrom=bad.example; dkim=pass header.d=example.com; dmarc=fail header.from=example.com",
            b"Content-Type: text/plain; charset=utf-8",
            b"",
            b"Please verify your account at https://example.com/login.",
        ]
    )

    result = use_case.execute(
        AnalyzeRawEmailCommand(
            email_bytes=email_bytes,
            suspicious_tlds={"zip"},
            allowed_url_schemes={"https"},
            known_shorteners={"bit.ly"},
            urgency_terms={"urgent"},
            financial_pressure_terms={"payment required"},
            credential_request_terms={"verify your account"},
            finding_weights={
                "DOMAIN_CONTAINS_PUNYCODE": 30,
                "DOMAIN_HAS_SUSPICIOUS_TLD": 20,
                "URL_HAS_EMBEDDED_CREDENTIALS": 25,
                "AUTHENTICATION_DMARC_FAILED": 50,
                "SOCIAL_ENGINEERING_HAS_URGENCY_TERMS": 10,
                "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS": 25,
            },
            critical_indicators={"AUTHENTICATION_DMARC_FAILED"},
        )
    )

    assert result.technical_analysis.domain_analysis.domain == "xn--paypl-3ve.zip"
    assert result.technical_analysis.url_analyses[0].url == "https://example.com/login"
    assert result.technical_analysis.authentication_analysis.dmarc_result == "fail"
    assert result.text_analysis.analyzed_text == (
        "Urgent account notice\n"
        "Please verify your account at https://example.com/login."
    )
    assert result.finding_codes == (
        "DOMAIN_CONTAINS_PUNYCODE",
        "DOMAIN_HAS_SUSPICIOUS_TLD",
        "AUTHENTICATION_SPF_FAILED",
        "AUTHENTICATION_DMARC_FAILED",
        "AUTHENTICATION_HAS_MULTIPLE_FAILURES",
        "SOCIAL_ENGINEERING_HAS_URGENCY_TERMS",
        "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS",
    )
    assert result.finding_code_summary.highest_severity == "CRITICAL"
    assert result.risk_score.risk_level == "CRITICAL"
    assert result.risk_score.has_critical_indicators is True
