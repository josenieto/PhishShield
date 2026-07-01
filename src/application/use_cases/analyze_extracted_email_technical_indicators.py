from dataclasses import dataclass

from application.models.extracted_email import ExtractedEmailContent
from application.use_cases.analyze_attachment_indicators import (
    AnalyzeAttachmentIndicatorsCommand,
    AnalyzeAttachmentIndicatorsUseCase,
    AttachmentIndicatorsAnalysis,
)
from application.use_cases.analyze_authentication_indicators import (
    AnalyzeAuthenticationIndicatorsCommand,
    AnalyzeAuthenticationIndicatorsUseCase,
    AuthenticationIndicatorsAnalysis,
)
from application.use_cases.analyze_domain_indicators import (
    AnalyzeDomainIndicatorsCommand,
    AnalyzeDomainIndicatorsUseCase,
    DomainIndicatorsAnalysis,
)
from application.use_cases.analyze_url_indicators import (
    AnalyzeUrlIndicatorsCommand,
    AnalyzeUrlIndicatorsUseCase,
    UrlIndicatorsAnalysis,
)


@dataclass(frozen=True)
class AnalyzeExtractedEmailTechnicalIndicatorsCommand:
    extracted_email: ExtractedEmailContent
    suspicious_tlds: set[str]
    allowed_url_schemes: set[str]
    known_shorteners: set[str]
    max_subdomain_depth: int = 4
    query_density_threshold: int = 3


@dataclass(frozen=True)
class ExtractedEmailTechnicalIndicatorsAnalysis:
    domain_analysis: DomainIndicatorsAnalysis
    url_analyses: tuple[UrlIndicatorsAnalysis, ...]
    attachment_analyses: tuple[AttachmentIndicatorsAnalysis, ...]
    authentication_analysis: AuthenticationIndicatorsAnalysis
    finding_codes: tuple[str, ...]


class AnalyzeExtractedEmailTechnicalIndicatorsUseCase:
    def execute(
        self,
        command: AnalyzeExtractedEmailTechnicalIndicatorsCommand,
    ) -> ExtractedEmailTechnicalIndicatorsAnalysis:
        extracted_email = command.extracted_email

        domain_analysis = AnalyzeDomainIndicatorsUseCase().execute(
            AnalyzeDomainIndicatorsCommand(
                domain=extracted_email.sender_domain,
                suspicious_tlds=command.suspicious_tlds,
                max_subdomain_depth=command.max_subdomain_depth,
            )
        )
        url_analyses = tuple(
            AnalyzeUrlIndicatorsUseCase().execute(
                AnalyzeUrlIndicatorsCommand(
                    url=url,
                    allowed_schemes=command.allowed_url_schemes,
                    known_shorteners=command.known_shorteners,
                    query_density_threshold=command.query_density_threshold,
                )
            )
            for url in extracted_email.urls
        )
        attachment_analyses = tuple(
            AnalyzeAttachmentIndicatorsUseCase().execute(
                AnalyzeAttachmentIndicatorsCommand(filename=filename)
            )
            for filename in extracted_email.attachment_filenames
        )
        authentication_analysis = AnalyzeAuthenticationIndicatorsUseCase().execute(
            AnalyzeAuthenticationIndicatorsCommand(
                spf_result=extracted_email.spf_result,
                dkim_result=extracted_email.dkim_result,
                dmarc_result=extracted_email.dmarc_result,
            )
        )

        return ExtractedEmailTechnicalIndicatorsAnalysis(
            domain_analysis=domain_analysis,
            url_analyses=url_analyses,
            attachment_analyses=attachment_analyses,
            authentication_analysis=authentication_analysis,
            finding_codes=_collect_finding_codes(
                domain_analysis,
                url_analyses,
                attachment_analyses,
                authentication_analysis,
            ),
        )


def _collect_finding_codes(
    domain_analysis: DomainIndicatorsAnalysis,
    url_analyses: tuple[UrlIndicatorsAnalysis, ...],
    attachment_analyses: tuple[AttachmentIndicatorsAnalysis, ...],
    authentication_analysis: AuthenticationIndicatorsAnalysis,
) -> tuple[str, ...]:
    return tuple(
        [
            *domain_analysis.findings,
            *(finding for analysis in url_analyses for finding in analysis.findings),
            *(
                finding
                for analysis in attachment_analyses
                for finding in analysis.findings
            ),
            *authentication_analysis.findings,
        ]
    )
