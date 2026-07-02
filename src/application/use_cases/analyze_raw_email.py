from dataclasses import dataclass

from application.ports.outbound.email_content_extractor import EmailContentExtractorPort
from application.use_cases.analyze_extracted_email import (
    AnalyzeExtractedEmailCommand,
    AnalyzeExtractedEmailUseCase,
    ExtractedEmailAnalysis,
)


@dataclass(frozen=True)
class AnalyzeRawEmailCommand:
    email_bytes: bytes
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


class AnalyzeRawEmailUseCase:
    def __init__(self, email_content_extractor: EmailContentExtractorPort) -> None:
        self._email_content_extractor = email_content_extractor

    def execute(self, command: AnalyzeRawEmailCommand) -> ExtractedEmailAnalysis:
        extracted_email = self._email_content_extractor.extract(command.email_bytes)

        return AnalyzeExtractedEmailUseCase().execute(
            AnalyzeExtractedEmailCommand(
                extracted_email=extracted_email,
                suspicious_tlds=command.suspicious_tlds,
                allowed_url_schemes=command.allowed_url_schemes,
                known_shorteners=command.known_shorteners,
                urgency_terms=command.urgency_terms,
                financial_pressure_terms=command.financial_pressure_terms,
                credential_request_terms=command.credential_request_terms,
                finding_weights=command.finding_weights,
                critical_indicators=command.critical_indicators,
                max_subdomain_depth=command.max_subdomain_depth,
                query_density_threshold=command.query_density_threshold,
            )
        )
