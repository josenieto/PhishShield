from dataclasses import dataclass

from application.models.extracted_email import ExtractedEmailContent
from application.use_cases.analyze_social_engineering_indicators import (
    AnalyzeSocialEngineeringIndicatorsCommand,
    AnalyzeSocialEngineeringIndicatorsUseCase,
    SocialEngineeringIndicatorsAnalysis,
)


@dataclass(frozen=True)
class AnalyzeExtractedEmailTextIndicatorsCommand:
    extracted_email: ExtractedEmailContent
    urgency_terms: set[str]
    financial_pressure_terms: set[str]
    credential_request_terms: set[str]


@dataclass(frozen=True)
class ExtractedEmailTextIndicatorsAnalysis:
    analyzed_text: str
    social_engineering_analysis: SocialEngineeringIndicatorsAnalysis
    finding_codes: tuple[str, ...]


class AnalyzeExtractedEmailTextIndicatorsUseCase:
    def execute(
        self,
        command: AnalyzeExtractedEmailTextIndicatorsCommand,
    ) -> ExtractedEmailTextIndicatorsAnalysis:
        analyzed_text = _join_subject_and_body(
            command.extracted_email.subject,
            command.extracted_email.body_text,
        )
        social_engineering_analysis = AnalyzeSocialEngineeringIndicatorsUseCase().execute(
            AnalyzeSocialEngineeringIndicatorsCommand(
                text=analyzed_text,
                urgency_terms=command.urgency_terms,
                financial_pressure_terms=command.financial_pressure_terms,
                credential_request_terms=command.credential_request_terms,
            )
        )

        return ExtractedEmailTextIndicatorsAnalysis(
            analyzed_text=analyzed_text,
            social_engineering_analysis=social_engineering_analysis,
            finding_codes=tuple(social_engineering_analysis.findings),
        )


def _join_subject_and_body(subject: str, body_text: str) -> str:
    return "\n".join(
        text_part
        for text_part in (subject, body_text)
        if text_part
    )
