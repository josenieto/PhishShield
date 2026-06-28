from dataclasses import dataclass

from domain.services.social_engineering.text_signals import (
    classify_social_engineering_risk,
    contains_credential_request_terms,
    contains_financial_pressure_terms,
    contains_urgency_terms,
    count_social_engineering_signals,
)


SOCIAL_ENGINEERING_HAS_URGENCY_TERMS = "SOCIAL_ENGINEERING_HAS_URGENCY_TERMS"
SOCIAL_ENGINEERING_HAS_FINANCIAL_PRESSURE_TERMS = (
    "SOCIAL_ENGINEERING_HAS_FINANCIAL_PRESSURE_TERMS"
)
SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS = (
    "SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS"
)


@dataclass(frozen=True)
class AnalyzeSocialEngineeringIndicatorsCommand:
    text: str
    urgency_terms: set[str]
    financial_pressure_terms: set[str]
    credential_request_terms: set[str]


@dataclass(frozen=True)
class SocialEngineeringIndicatorsAnalysis:
    text: str
    has_urgency_terms: bool
    has_financial_pressure_terms: bool
    has_credential_request_terms: bool
    signal_counts: dict[str, int]
    risk_level: str
    findings: list[str]


class AnalyzeSocialEngineeringIndicatorsUseCase:
    def execute(
        self,
        command: AnalyzeSocialEngineeringIndicatorsCommand,
    ) -> SocialEngineeringIndicatorsAnalysis:
        text = command.text
        social_engineering_has_urgency_terms = contains_urgency_terms(
            text,
            command.urgency_terms,
        )
        social_engineering_has_financial_pressure_terms = (
            contains_financial_pressure_terms(
                text,
                command.financial_pressure_terms,
            )
        )
        social_engineering_has_credential_request_terms = (
            contains_credential_request_terms(
                text,
                command.credential_request_terms,
            )
        )
        signal_counts = count_social_engineering_signals(
            text,
            {
                "urgency": command.urgency_terms,
                "financial_pressure": command.financial_pressure_terms,
                "credential_request": command.credential_request_terms,
            },
        )
        finding_conditions = [
            (
                social_engineering_has_urgency_terms,
                SOCIAL_ENGINEERING_HAS_URGENCY_TERMS,
            ),
            (
                social_engineering_has_financial_pressure_terms,
                SOCIAL_ENGINEERING_HAS_FINANCIAL_PRESSURE_TERMS,
            ),
            (
                social_engineering_has_credential_request_terms,
                SOCIAL_ENGINEERING_HAS_CREDENTIAL_REQUEST_TERMS,
            ),
        ]

        return SocialEngineeringIndicatorsAnalysis(
            text=text,
            has_urgency_terms=social_engineering_has_urgency_terms,
            has_financial_pressure_terms=social_engineering_has_financial_pressure_terms,
            has_credential_request_terms=social_engineering_has_credential_request_terms,
            signal_counts=signal_counts,
            risk_level=classify_social_engineering_risk(signal_counts),
            findings=[
                finding
                for condition, finding in finding_conditions
                if condition
            ],
        )
