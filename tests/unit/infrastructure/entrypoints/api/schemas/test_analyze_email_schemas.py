from application.models.extracted_email import ExtractedEmailContent
from application.use_cases.analyze_extracted_email import ExtractedEmailAnalysis
from application.use_cases.calculate_risk_score import RiskScoreAnalysis
from application.use_cases.summarize_analysis_findings import AnalysisFindingsSummary
from domain.value_objects.finding import (
    FINDING_CATEGORY_AUTHENTICATION,
    FINDING_CATEGORY_DOMAIN,
    FINDING_SEVERITY_CRITICAL,
    FINDING_SEVERITY_HIGH,
    Finding,
)
from infrastructure.entrypoints.api.schemas.analyze_email import (
    AnalyzeEmailResponse,
    AuthenticationResultsResponse,
    ExtractedEvidenceResponse,
    FindingResponse,
    FindingSummaryResponse,
    RiskScoreResponse,
    extracted_email_analysis_to_response,
    extracted_evidence_to_response,
    finding_summary_to_response,
    finding_to_response,
    risk_score_to_response,
)


def test_should_convert_finding_to_response() -> None:
    response = finding_to_response(
        Finding(
            code="DOMAIN_CONTAINS_PUNYCODE",
            category=FINDING_CATEGORY_DOMAIN,
            severity=FINDING_SEVERITY_HIGH,
        )
    )

    assert response == FindingResponse(
        code="DOMAIN_CONTAINS_PUNYCODE",
        category=FINDING_CATEGORY_DOMAIN,
        severity=FINDING_SEVERITY_HIGH,
    )


def test_should_convert_finding_summary_to_response() -> None:
    domain_finding = Finding(
        code="DOMAIN_CONTAINS_PUNYCODE",
        category=FINDING_CATEGORY_DOMAIN,
        severity=FINDING_SEVERITY_HIGH,
    )
    authentication_finding = Finding(
        code="AUTHENTICATION_DMARC_FAILED",
        category=FINDING_CATEGORY_AUTHENTICATION,
        severity=FINDING_SEVERITY_CRITICAL,
    )
    summary = AnalysisFindingsSummary(
        findings=[domain_finding, authentication_finding],
        sorted_findings=[authentication_finding, domain_finding],
        finding_counts_by_category={
            FINDING_CATEGORY_DOMAIN: 1,
            FINDING_CATEGORY_AUTHENTICATION: 1,
        },
        highest_severity=FINDING_SEVERITY_CRITICAL,
        total_findings=2,
    )

    response = finding_summary_to_response(summary)

    assert response == FindingSummaryResponse(
        findings=[
            FindingResponse(
                code="DOMAIN_CONTAINS_PUNYCODE",
                category=FINDING_CATEGORY_DOMAIN,
                severity=FINDING_SEVERITY_HIGH,
            ),
            FindingResponse(
                code="AUTHENTICATION_DMARC_FAILED",
                category=FINDING_CATEGORY_AUTHENTICATION,
                severity=FINDING_SEVERITY_CRITICAL,
            ),
        ],
        sorted_findings=[
            FindingResponse(
                code="AUTHENTICATION_DMARC_FAILED",
                category=FINDING_CATEGORY_AUTHENTICATION,
                severity=FINDING_SEVERITY_CRITICAL,
            ),
            FindingResponse(
                code="DOMAIN_CONTAINS_PUNYCODE",
                category=FINDING_CATEGORY_DOMAIN,
                severity=FINDING_SEVERITY_HIGH,
            ),
        ],
        finding_counts_by_category={
            FINDING_CATEGORY_DOMAIN: 1,
            FINDING_CATEGORY_AUTHENTICATION: 1,
        },
        highest_severity=FINDING_SEVERITY_CRITICAL,
        total_findings=2,
    )


def test_should_convert_risk_score_to_response() -> None:
    risk_score = RiskScoreAnalysis(
        indicators=["DOMAIN_CONTAINS_PUNYCODE", "AUTHENTICATION_DMARC_FAILED"],
        raw_score=80,
        capped_score=80,
        risk_level="CRITICAL",
        has_critical_indicators=True,
    )

    assert risk_score_to_response(risk_score) == RiskScoreResponse(
        indicators=["DOMAIN_CONTAINS_PUNYCODE", "AUTHENTICATION_DMARC_FAILED"],
        raw_score=80,
        capped_score=80,
        risk_level="CRITICAL",
        has_critical_indicators=True,
    )


def test_should_convert_extracted_evidence_to_response() -> None:
    extracted_email = ExtractedEmailContent(
        sender_domain="example.com",
        urls=("https://example.com/login",),
        attachment_filenames=("invoice.pdf",),
        subject="Weekly account summary",
        body_text="Body text.",
        spf_result="pass",
        dkim_result="pass",
        dmarc_result="pass",
    )

    assert extracted_evidence_to_response(extracted_email) == ExtractedEvidenceResponse(
        sender_domain="example.com",
        subject="Weekly account summary",
        urls=["https://example.com/login"],
        attachment_filenames=["invoice.pdf"],
        authentication_results=AuthenticationResultsResponse(
            spf_result="pass",
            dkim_result="pass",
            dmarc_result="pass",
        ),
    )


def test_should_convert_extracted_email_analysis_to_response() -> None:
    extracted_email = ExtractedEmailContent(
        sender_domain="example.com",
        urls=("https://example.com/login",),
        attachment_filenames=("invoice.pdf",),
        subject="Weekly account summary",
        body_text="Body text.",
        spf_result="pass",
        dkim_result="pass",
        dmarc_result="pass",
    )
    finding = Finding(
        code="AUTHENTICATION_DMARC_FAILED",
        category=FINDING_CATEGORY_AUTHENTICATION,
        severity=FINDING_SEVERITY_CRITICAL,
    )
    analysis = ExtractedEmailAnalysis(
        extracted_email=extracted_email,
        technical_analysis=None,
        text_analysis=None,
        finding_codes=("AUTHENTICATION_DMARC_FAILED", "AUTHENTICATION_DMARC_FAILED"),
        unique_finding_codes=("AUTHENTICATION_DMARC_FAILED",),
        finding_code_summary=AnalysisFindingsSummary(
            findings=[finding],
            sorted_findings=[finding],
            finding_counts_by_category={FINDING_CATEGORY_AUTHENTICATION: 1},
            highest_severity=FINDING_SEVERITY_CRITICAL,
            total_findings=1,
        ),
        risk_score=RiskScoreAnalysis(
            indicators=["AUTHENTICATION_DMARC_FAILED"],
            raw_score=50,
            capped_score=50,
            risk_level="HIGH",
            has_critical_indicators=True,
        ),
    )

    response = extracted_email_analysis_to_response(analysis)

    assert response == AnalyzeEmailResponse(
        finding_codes=["AUTHENTICATION_DMARC_FAILED", "AUTHENTICATION_DMARC_FAILED"],
        unique_finding_codes=["AUTHENTICATION_DMARC_FAILED"],
        finding_summary=FindingSummaryResponse(
            findings=[
                FindingResponse(
                    code="AUTHENTICATION_DMARC_FAILED",
                    category=FINDING_CATEGORY_AUTHENTICATION,
                    severity=FINDING_SEVERITY_CRITICAL,
                )
            ],
            sorted_findings=[
                FindingResponse(
                    code="AUTHENTICATION_DMARC_FAILED",
                    category=FINDING_CATEGORY_AUTHENTICATION,
                    severity=FINDING_SEVERITY_CRITICAL,
                )
            ],
            finding_counts_by_category={FINDING_CATEGORY_AUTHENTICATION: 1},
            highest_severity=FINDING_SEVERITY_CRITICAL,
            total_findings=1,
        ),
        risk_score=RiskScoreResponse(
            indicators=["AUTHENTICATION_DMARC_FAILED"],
            raw_score=50,
            capped_score=50,
            risk_level="HIGH",
            has_critical_indicators=True,
        ),
        extracted_evidence=ExtractedEvidenceResponse(
            sender_domain="example.com",
            subject="Weekly account summary",
            urls=["https://example.com/login"],
            attachment_filenames=["invoice.pdf"],
            authentication_results=AuthenticationResultsResponse(
                spf_result="pass",
                dkim_result="pass",
                dmarc_result="pass",
            ),
        ),
    )
