from pydantic import BaseModel

from application.use_cases.analyze_extracted_email import ExtractedEmailAnalysis
from application.use_cases.calculate_risk_score import RiskScoreAnalysis
from application.use_cases.summarize_analysis_findings import AnalysisFindingsSummary
from domain.value_objects.finding import Finding


class FindingResponse(BaseModel):
    code: str
    category: str
    severity: str


class FindingSummaryResponse(BaseModel):
    findings: list[FindingResponse]
    sorted_findings: list[FindingResponse]
    finding_counts_by_category: dict[str, int]
    highest_severity: str
    total_findings: int


class RiskScoreResponse(BaseModel):
    indicators: list[str]
    raw_score: int
    capped_score: int
    risk_level: str
    has_critical_indicators: bool


class AnalyzeEmailResponse(BaseModel):
    finding_codes: list[str]
    unique_finding_codes: list[str]
    finding_summary: FindingSummaryResponse
    risk_score: RiskScoreResponse


def finding_to_response(finding: Finding) -> FindingResponse:
    return FindingResponse(
        code=finding.code,
        category=finding.category,
        severity=finding.severity,
    )


def finding_summary_to_response(
    summary: AnalysisFindingsSummary,
) -> FindingSummaryResponse:
    return FindingSummaryResponse(
        findings=[finding_to_response(finding) for finding in summary.findings],
        sorted_findings=[
            finding_to_response(finding)
            for finding in summary.sorted_findings
        ],
        finding_counts_by_category=summary.finding_counts_by_category,
        highest_severity=summary.highest_severity,
        total_findings=summary.total_findings,
    )


def risk_score_to_response(risk_score: RiskScoreAnalysis) -> RiskScoreResponse:
    return RiskScoreResponse(
        indicators=risk_score.indicators,
        raw_score=risk_score.raw_score,
        capped_score=risk_score.capped_score,
        risk_level=risk_score.risk_level,
        has_critical_indicators=risk_score.has_critical_indicators,
    )


def extracted_email_analysis_to_response(
    analysis: ExtractedEmailAnalysis,
) -> AnalyzeEmailResponse:
    return AnalyzeEmailResponse(
        finding_codes=list(analysis.finding_codes),
        unique_finding_codes=list(analysis.unique_finding_codes),
        finding_summary=finding_summary_to_response(analysis.finding_code_summary),
        risk_score=risk_score_to_response(analysis.risk_score),
    )
