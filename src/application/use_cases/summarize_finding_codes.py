from dataclasses import dataclass

from application.use_cases.summarize_analysis_findings import (
    AnalysisFindingsSummary,
    SummarizeAnalysisFindingsCommand,
    SummarizeAnalysisFindingsUseCase,
)
from domain.services.finding_analysis.finding_definitions import (
    build_findings_from_codes,
)


@dataclass(frozen=True)
class SummarizeFindingCodesCommand:
    finding_codes: list[str]


class SummarizeFindingCodesUseCase:
    def execute(
        self,
        command: SummarizeFindingCodesCommand,
    ) -> AnalysisFindingsSummary:
        findings = build_findings_from_codes(command.finding_codes)

        return SummarizeAnalysisFindingsUseCase().execute(
            SummarizeAnalysisFindingsCommand(findings=findings)
        )
