import type { AnalyzeEmailResponse, FindingResponse } from "../types/api";

import { displayValue, groupFindingsByCategory } from "../components/analysis-results/shared";


type CreateMarkdownReportParams = {
  analysis: AnalyzeEmailResponse;
  selectedFileName: string;
};


const MARKDOWN_SPECIAL_CHARACTERS = /([\\`*_{}\[\]()#+\-!>|])/g;


function sanitizeMarkdownValue(value: string): string {
  return value
    .replace(/[\r\n\t]+/g, " ")
    .replace(/\s{2,}/g, " ")
    .trim()
    .replace(MARKDOWN_SPECIAL_CHARACTERS, "\\$1");
}


function formatDisplayValue(value: string): string {
  return sanitizeMarkdownValue(displayValue(value));
}


function formatList(items: string[], emptyLabel: string): string[] {
  if (items.length === 0) {
    return [`- ${sanitizeMarkdownValue(emptyLabel)}`];
  }

  return items.map((item) => `- ${sanitizeMarkdownValue(item)}`);
}


function formatFinding(finding: FindingResponse): string[] {
  return [
    `- ${sanitizeMarkdownValue(finding.code)} [${sanitizeMarkdownValue(finding.severity)}]`,
    `  Category: ${sanitizeMarkdownValue(finding.category)}`,
    `  Explanation: ${sanitizeMarkdownValue(finding.explanation)}`,
  ];
}


export function createMarkdownReport({ analysis, selectedFileName }: CreateMarkdownReportParams): string {
  const groupedFindings = groupFindingsByCategory(analysis);

  const lines = [
    "# PhishShield Analysis Report",
    "",
    "## Overview",
    `- File: ${sanitizeMarkdownValue(selectedFileName)}`,
    `- Risk level: ${analysis.risk_score.risk_level}`,
    `- Raw score: ${analysis.risk_score.raw_score}`,
    `- Capped score: ${analysis.risk_score.capped_score}`,
    `- Critical indicators: ${analysis.risk_score.has_critical_indicators ? "Present" : "Not observed"}`,
    `- Highest severity: ${analysis.finding_summary.highest_severity}`,
    `- Total findings: ${analysis.finding_summary.total_findings}`,
    `- Unique finding codes: ${analysis.unique_finding_codes.length}`,
    "",
    "## Extracted Evidence",
    `- Sender domain: ${formatDisplayValue(analysis.extracted_evidence.sender_domain)}`,
    `- Subject: ${formatDisplayValue(analysis.extracted_evidence.subject)}`,
    "",
    "### URLs",
    ...formatList(analysis.extracted_evidence.urls, "No URLs extracted"),
    "",
    "### Attachments",
    ...formatList(analysis.extracted_evidence.attachment_filenames, "No attachments extracted"),
    "",
    "### Authentication Results",
    `- SPF: ${formatDisplayValue(analysis.extracted_evidence.authentication_results.spf_result)}`,
    `- DKIM: ${formatDisplayValue(analysis.extracted_evidence.authentication_results.dkim_result)}`,
    `- DMARC: ${formatDisplayValue(analysis.extracted_evidence.authentication_results.dmarc_result)}`,
    "",
    "## Findings By Category",
  ];

  if (groupedFindings.length === 0) {
    lines.push("- No findings returned by the backend.");
  } else {
    for (const [category, findings] of groupedFindings) {
      lines.push("");
      lines.push(`### ${sanitizeMarkdownValue(category)}`);
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
