from dataclasses import dataclass

from domain.services.authentication_analysis.authentication_results import (
    classify_authentication_risk,
    has_authentication_failure,
    is_authentication_aligned,
    summarize_authentication_findings,
)


@dataclass(frozen=True)
class AnalyzeAuthenticationIndicatorsCommand:
    spf_result: str
    dkim_result: str
    dmarc_result: str


@dataclass(frozen=True)
class AuthenticationIndicatorsAnalysis:
    spf_result: str
    dkim_result: str
    dmarc_result: str
    is_aligned: bool
    has_failure: bool
    risk_level: str
    findings: list[str]


class AnalyzeAuthenticationIndicatorsUseCase:
    def execute(
        self,
        command: AnalyzeAuthenticationIndicatorsCommand,
    ) -> AuthenticationIndicatorsAnalysis:
        spf_result = command.spf_result
        dkim_result = command.dkim_result
        dmarc_result = command.dmarc_result

        return AuthenticationIndicatorsAnalysis(
            spf_result=spf_result,
            dkim_result=dkim_result,
            dmarc_result=dmarc_result,
            is_aligned=is_authentication_aligned(
                spf_result,
                dkim_result,
                dmarc_result,
            ),
            has_failure=has_authentication_failure(
                spf_result,
                dkim_result,
                dmarc_result,
            ),
            risk_level=classify_authentication_risk(
                spf_result,
                dkim_result,
                dmarc_result,
            ),
            findings=summarize_authentication_findings(
                spf_result,
                dkim_result,
                dmarc_result,
            ),
        )
