import type { AnalyzeEmailResponse, FindingResponse } from "../types/api";

import { displayValue, groupFindingsByCategory } from "../components/analysis-results/shared";


type CreateMarkdownReportParams = {
  analysis: AnalyzeEmailResponse;
  selectedFileName: string;
};


function formatList(items: string[], emptyLabel: string): string[] {
  if (items.length === 0) {
    return [`- ${emptyLabel}`];
  }

  return items.map((item) => `- ${item}`);
}


function formatFinding(finding: FindingResponse): string[] {
  return [
    `- ${finding.code} [${finding.severity}]`,
    `  Category: ${finding.category}`,
    `  Explanation: ${finding.explanation}`,
  ];
}


export function createMarkdownReport({ analysis, selectedFileName }: CreateMarkdownReportParams): string {
  const groupedFindings = groupFindingsByCategory(analysis);

  const lines = [
    "# PhishShield Analysis Report",
    "",
    "## Overview",
    `- File: ${selectedFileName}`,
    `- Risk level: ${analysis.risk_score.risk_level}`,
    `- Raw score: ${analysis.risk_score.raw_score}`,
    `- Capped score: ${analysis.risk_score.capped_score}`,
    `- Critical indicators: ${analysis.risk_score.has_critical_indicators ? "Present" : "Not observed"}`,
    `- Highest severity: ${analysis.finding_summary.highest_severity}`,
    `- Total findings: ${analysis.finding_summary.total_findings}`,
    `- Unique finding codes: ${analysis.unique_finding_codes.length}`,
    "",
    "## Extracted Evidence",
    `- Sender domain: ${displayValue(analysis.extracted_evidence.sender_domain)}`,
    `- Subject: ${displayValue(analysis.extracted_evidence.subject)}`,
    "",
    "### URLs",
    ...formatList(analysis.extracted_evidence.urls, "No URLs extracted"),
    "",
    "### Attachments",
    ...formatList(analysis.extracted_evidence.attachment_filenames, "No attachments extracted"),
    "",
    "### Authentication Results",
    `- SPF: ${displayValue(analysis.extracted_evidence.authentication_results.spf_result)}`,
    `- DKIM: ${displayValue(analysis.extracted_evidence.authentication_results.dkim_result)}`,
    `- DMARC: ${displayValue(analysis.extracted_evidence.authentication_results.dmarc_result)}`,
    "",
    "## Findings By Category",
  ];

  if (groupedFindings.length === 0) {
    lines.push("- No findings returned by the backend.");
  } else {
    for (const [category, findings] of groupedFindings) {
      lines.push("");
      lines.push(`### ${category}`);
      lines.push(`- Count: ${findings.length}`);
      lines.push("");

      for (const finding of findings) {
        lines.push(...formatFinding(finding));
      }
    }
  }

  lines.push("");
  lines.push("## Unique Indicator Codes");
  lines.push(...formatList(analysis.unique_finding_codes, "No findings"));

  return `${lines.join("\n")}\n`;
}
