from dataclasses import dataclass

from application.models.extracted_email import ExtractedEmailContent
from application.use_cases.analyze_extracted_email_technical_indicators import (
    AnalyzeExtractedEmailTechnicalIndicatorsCommand,
    AnalyzeExtractedEmailTechnicalIndicatorsUseCase,
    ExtractedEmailTechnicalIndicatorsAnalysis,
)
from application.use_cases.analyze_extracted_email_text_indicators import (
    AnalyzeExtractedEmailTextIndicatorsCommand,
    AnalyzeExtractedEmailTextIndicatorsUseCase,
    ExtractedEmailTextIndicatorsAnalysis,
)
from application.use_cases.calculate_risk_score import (
    CalculateRiskScoreCommand,
    CalculateRiskScoreUseCase,
    RiskScoreAnalysis,
)
from application.use_cases.summarize_finding_codes import (
    SummarizeFindingCodesCommand,
    SummarizeFindingCodesUseCase,
)
from application.use_cases.summarize_analysis_findings import AnalysisFindingsSummary
from domain.services.finding_analysis.findings import deduplicate_finding_codes


@dataclass(frozen=True)
class AnalyzeExtractedEmailCommand:
    extracted_email: ExtractedEmailContent
    suspicious_tlds: set[str]
    allowed_url_schemes: set[str]
    known_shorteners: set[str]
    urgency_terms: set[str]
    financial_pressure_terms: set[str]
    credential_request_terms: set[str]
    finding_weights: dict[str, int]
    critical_indicators: set[str]
    max_subdomain_depth: int = 4
    query_density_threshold: int = 3


@dataclass(frozen=True)
class ExtractedEmailAnalysis:
    technical_analysis: ExtractedEmailTechnicalIndicatorsAnalysis
    text_analysis: ExtractedEmailTextIndicatorsAnalysis
    finding_codes: tuple[str, ...]
    unique_finding_codes: tuple[str, ...]
    finding_code_summary: AnalysisFindingsSummary
    risk_score: RiskScoreAnalysis


class AnalyzeExtractedEmailUseCase:
    def execute(self, command: AnalyzeExtractedEmailCommand) -> ExtractedEmailAnalysis:
        technical_analysis = AnalyzeExtractedEmailTechnicalIndicatorsUseCase().execute(
            AnalyzeExtractedEmailTechnicalIndicatorsCommand(
                extracted_email=command.extracted_email,
                suspicious_tlds=command.suspicious_tlds,
                allowed_url_schemes=command.allowed_url_schemes,
                known_shorteners=command.known_shorteners,
                max_subdomain_depth=command.max_subdomain_depth,
                query_density_threshold=command.query_density_threshold,
            )
        )
        text_analysis = AnalyzeExtractedEmailTextIndicatorsUseCase().execute(
            AnalyzeExtractedEmailTextIndicatorsCommand(
                extracted_email=command.extracted_email,
                urgency_terms=command.urgency_terms,
                financial_pressure_terms=command.financial_pressure_terms,
                credential_request_terms=command.credential_request_terms,
            )
        )
        finding_codes = technical_analysis.finding_codes + text_analysis.finding_codes
        unique_finding_codes = tuple(deduplicate_finding_codes(list(finding_codes)))
        finding_code_summary = SummarizeFindingCodesUseCase().execute(
            SummarizeFindingCodesCommand(finding_codes=list(unique_finding_codes))
        )
        risk_score = CalculateRiskScoreUseCase().execute(
            CalculateRiskScoreCommand(
                indicators=list(unique_finding_codes),
                weights=command.finding_weights,
                critical_indicators=command.critical_indicators,
            )
        )

        return ExtractedEmailAnalysis(
            technical_analysis=technical_analysis,
            text_analysis=text_analysis,
            finding_codes=finding_codes,
            unique_finding_codes=unique_finding_codes,
            finding_code_summary=finding_code_summary,
            risk_score=risk_score,
        )
