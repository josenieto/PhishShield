from dataclasses import dataclass

from domain.services.finding_analysis.findings import (
    count_findings_by_category,
    get_highest_finding_severity,
    sort_findings_by_severity,
)
from domain.value_objects.finding import Finding


@dataclass(frozen=True)
class SummarizeAnalysisFindingsCommand:
    findings: list[Finding]


@dataclass(frozen=True)
class AnalysisFindingsSummary:
    findings: list[Finding]
    sorted_findings: list[Finding]
    finding_counts_by_category: dict[str, int]
    highest_severity: str
    total_findings: int


class SummarizeAnalysisFindingsUseCase:
    def execute(
        self,
        command: SummarizeAnalysisFindingsCommand,
    ) -> AnalysisFindingsSummary:
        findings = command.findings

        return AnalysisFindingsSummary(
            findings=findings,
            sorted_findings=sort_findings_by_severity(findings),
            finding_counts_by_category=count_findings_by_category(findings),
            highest_severity=get_highest_finding_severity(findings),
            total_findings=len(findings),
        )
