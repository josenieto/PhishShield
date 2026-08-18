import type { AnalyzeEmailResponse, FindingResponse } from "../types/api";

import { displayValue, groupFindingsByCategory, riskPostureHint } from "../components/analysis-results/shared";
import { formatRiskScore, formatRiskScoreDetails } from "../formatRiskScore";


type CreateHtmlReportParams = {
  analysis: AnalyzeEmailResponse;
  selectedFileName: string;
};


function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}


function formatList(items: string[], emptyLabel: string): string {
  if (items.length === 0) {
    return `<li>${escapeHtml(emptyLabel)}</li>`;
  }

  return items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}


function formatFinding(finding: FindingResponse): string {
  return [
    "<li>",
    `<strong>${escapeHtml(finding.code)}</strong> <span>[${escapeHtml(finding.severity)}]</span>`,
    `<div>Category: ${escapeHtml(finding.category)}</div>`,
    `<div>Explanation: ${escapeHtml(finding.explanation)}</div>`,
    "</li>",
  ].join("");
}


export function createHtmlReport({ analysis, selectedFileName }: CreateHtmlReportParams): string {
  const groupedFindings = groupFindingsByCategory(analysis);
  const groupedFindingsHtml = groupedFindings.length === 0
    ? "<p>No findings returned by the backend.</p>"
    : groupedFindings.map(([category, findings]) => [
        "<section>",
        `<h3>${escapeHtml(category)}</h3>`,
        `<p>Count: ${findings.length}</p>`,
        `<ul>${findings.map((finding) => formatFinding(finding)).join("")}</ul>`,
        "</section>",
      ].join("")).join("");

  return [
    "<!doctype html>",
    '<html lang="en">',
    "<head>",
    '  <meta charset="utf-8">',
    "  <title>PhishShield Analysis Report</title>",
    '  <meta name="viewport" content="width=device-width, initial-scale=1">',
    "  <style>",
    "    :root { color-scheme: dark; }",
    "    body { margin: 0; padding: 2rem; font-family: Inter, Arial, sans-serif; background: #0d1117; color: #f3f6ff; }",
    "    main { max-width: 1080px; margin: 0 auto; display: grid; gap: 1.5rem; }",
    "    section { padding: 1.25rem; border-radius: 16px; background: #111827; border: 1px solid rgba(148, 163, 184, 0.18); }",
    "    h1, h2, h3, p { margin-top: 0; }",
    "    ul { margin: 0; padding-left: 1.25rem; }",
    "    li { margin-bottom: 0.5rem; }",
    "    .grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }",
    "    .muted { color: #cbd5e1; }",
    "    code { font-family: 'Cascadia Code', Consolas, monospace; }",
    "  </style>",
    "</head>",
    "<body>",
    "  <main>",
    "    <section>",
    "      <h1>PhishShield Analysis Report</h1>",
    "      <p class=\"muted\">Exported from the current local analysis result.</p>",
    "    </section>",
    "    <section>",
    "      <h2>Overview</h2>",
    "      <ul>",
    `        <li>File: ${escapeHtml(selectedFileName)}</li>`,
    `        <li>Risk level: ${escapeHtml(analysis.risk_score.risk_level)}</li>`,
    `        <li>${formatRiskScore(analysis.risk_score)}</li>`,
    `        <li>${formatRiskScoreDetails(analysis.risk_score)}</li>`,
    `        <li>Critical indicators: ${analysis.risk_score.has_critical_indicators ? "Present" : "Not observed"}</li>`,
    `        <li>Highest severity: ${escapeHtml(analysis.finding_summary.highest_severity)}</li>`,
    `        <li>Total findings: ${analysis.finding_summary.total_findings}</li>`,
    `        <li>Unique finding codes: ${analysis.unique_finding_codes.length}</li>`,
    `        <li>Risk posture hint: ${escapeHtml(riskPostureHint(analysis))}</li>`,
    "      </ul>",
    "    </section>",
    "    <section>",
    "      <h2>Extracted Evidence</h2>",
    '      <div class="grid">',
    `        <div><strong>Sender domain</strong><p>${escapeHtml(displayValue(analysis.extracted_evidence.sender_domain))}</p></div>`,
    `        <div><strong>Subject</strong><p>${escapeHtml(displayValue(analysis.extracted_evidence.subject))}</p></div>`,
    "      </div>",
    "      <h3>URLs</h3>",
    `      <ul>${formatList(analysis.extracted_evidence.urls, "No URLs extracted")}</ul>`,
    "      <h3>Attachments</h3>",
    `      <ul>${formatList(analysis.extracted_evidence.attachment_filenames, "No attachments extracted")}</ul>`,
    "      <h3>Authentication Results</h3>",
    "      <ul>",
    `        <li>SPF: ${escapeHtml(displayValue(analysis.extracted_evidence.authentication_results.spf_result))}</li>`,
    `        <li>DKIM: ${escapeHtml(displayValue(analysis.extracted_evidence.authentication_results.dkim_result))}</li>`,
    `        <li>DMARC: ${escapeHtml(displayValue(analysis.extracted_evidence.authentication_results.dmarc_result))}</li>`,
    "      </ul>",
    "    </section>",
    "    <section>",
    "      <h2>Findings By Category</h2>",
    `      ${groupedFindingsHtml}`,
    "    </section>",
    "    <section>",
    "      <h2>Unique Indicator Codes</h2>",
    `      <ul>${formatList(analysis.unique_finding_codes, "No findings")}</ul>`,
    "    </section>",
    "  </main>",
    "</body>",
    "</html>",
  ].join("\n");
}
