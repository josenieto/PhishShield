import type { AnalyzeEmailResponse } from "../../types/api";


export function severityClassName(severity: string): string {
  return `severity-badge severity-${severity.toLowerCase()}`;
}


export function groupFindingsByCategory(analysis: AnalyzeEmailResponse) {
  const groupedFindings = new Map<string, AnalyzeEmailResponse["finding_summary"]["sorted_findings"]>();

  for (const finding of analysis.finding_summary.sorted_findings) {
    const currentFindings = groupedFindings.get(finding.category) ?? [];
    currentFindings.push(finding);
    groupedFindings.set(finding.category, currentFindings);
  }

  return Array.from(groupedFindings.entries());
}


export function sortedCategoryCounts(analysis: AnalyzeEmailResponse): Array<[string, number]> {
  return Object.entries(analysis.finding_summary.finding_counts_by_category).sort((left, right) => {
    if (right[1] !== left[1]) {
      return right[1] - left[1];
    }

    return left[0].localeCompare(right[0]);
  });
}


export function displayValue(value: string): string {
  return value.trim() === "" ? "Not available" : value;
}


export function riskPostureHint(analysis: AnalyzeEmailResponse): string {
  if (analysis.risk_score.has_critical_indicators) {
    return "Critical indicators are present and should be reviewed first.";
  }

  if (analysis.finding_summary.total_findings === 0) {
    return "No indicators were returned for the selected message.";
  }

  return "No critical indicators were observed, but the returned findings still require analyst review.";
}
