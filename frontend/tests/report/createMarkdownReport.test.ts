import { describe, expect, it } from "vitest";

import { createMarkdownReport } from "../../src/report/createMarkdownReport";


const SAMPLE_ANALYSIS = {
  finding_codes: [
    "AUTHENTICATION_RESULTS_UNKNOWN",
    "DOMAIN_HAS_SUSPICIOUS_TLD",
    "DOMAIN_CONTAINS_PUNYCODE",
  ],
  unique_finding_codes: [
    "AUTHENTICATION_RESULTS_UNKNOWN",
    "DOMAIN_HAS_SUSPICIOUS_TLD",
    "DOMAIN_CONTAINS_PUNYCODE",
  ],
  finding_summary: {
    findings: [
      {
        code: "AUTHENTICATION_RESULTS_UNKNOWN",
        category: "AUTHENTICATION",
        severity: "MEDIUM",
        explanation: "Authentication results were unavailable or could not be extracted, which reduces trust in sender validation.",
      },
      {
        code: "DOMAIN_HAS_SUSPICIOUS_TLD",
        category: "DOMAIN",
        severity: "MEDIUM",
        explanation: "The domain uses a top-level domain that is more commonly associated with abuse or impersonation.",
      },
      {
        code: "DOMAIN_CONTAINS_PUNYCODE",
        category: "DOMAIN",
        severity: "HIGH",
        explanation: "The domain contains Punycode, which can be used to create visually deceptive lookalike domains.",
      },
    ],
    sorted_findings: [
      {
        code: "DOMAIN_CONTAINS_PUNYCODE",
        category: "DOMAIN",
        severity: "HIGH",
        explanation: "The domain contains Punycode, which can be used to create visually deceptive lookalike domains.",
      },
      {
        code: "AUTHENTICATION_RESULTS_UNKNOWN",
        category: "AUTHENTICATION",
        severity: "MEDIUM",
        explanation: "Authentication results were unavailable or could not be extracted, which reduces trust in sender validation.",
      },
      {
        code: "DOMAIN_HAS_SUSPICIOUS_TLD",
        category: "DOMAIN",
        severity: "MEDIUM",
        explanation: "The domain uses a top-level domain that is more commonly associated with abuse or impersonation.",
      },
    ],
    finding_counts_by_category: {
      AUTHENTICATION: 1,
      DOMAIN: 2,
    },
    highest_severity: "HIGH",
    total_findings: 3,
  },
  risk_score: {
    indicators: [
      "AUTHENTICATION_RESULTS_UNKNOWN",
      "DOMAIN_HAS_SUSPICIOUS_TLD",
      "DOMAIN_CONTAINS_PUNYCODE",
    ],
    raw_score: 65,
    capped_score: 65,
    risk_level: "HIGH",
    has_critical_indicators: false,
  },
  extracted_evidence: {
    sender_domain: "example.zip",
    subject: "Urgent account notice",
    urls: ["https://example.com/login"],
    attachment_filenames: ["invoice.pdf.exe"],
    authentication_results: {
      spf_result: "fail",
      dkim_result: "pass",
      dmarc_result: "fail",
    },
  },
};


describe("createMarkdownReport", () => {
  it("should include the main sections and analysis values", () => {
    const report = createMarkdownReport({
      analysis: SAMPLE_ANALYSIS,
      selectedFileName: "security-review.eml",
    });

    expect(report).toContain("# PhishShield Analysis Report");
    expect(report).toContain("- File: security-review.eml");
    expect(report).toContain("- Risk level: HIGH");
    expect(report).toContain("- Raw score: 65");
    expect(report).toContain("- Critical indicators: Not observed");
    expect(report).toContain("## Extracted Evidence");
    expect(report).toContain("- Sender domain: example.zip");
    expect(report).toContain("### URLs");
    expect(report).toContain("- https://example.com/login");
    expect(report).toContain("### Authentication Results");
    expect(report).toContain("- SPF: fail");
    expect(report).toContain("## Findings By Category");
    expect(report).toContain("### DOMAIN");
    expect(report).toContain("- DOMAIN_CONTAINS_PUNYCODE [HIGH]");
    expect(report).toContain("Explanation: The domain contains Punycode");
    expect(report).toContain("## Unique Indicator Codes");
    expect(report).toContain("- DOMAIN_HAS_SUSPICIOUS_TLD");
  });

  it("should render empty placeholders when evidence lists are missing", () => {
    const report = createMarkdownReport({
      analysis: {
        ...SAMPLE_ANALYSIS,
        unique_finding_codes: [],
        finding_summary: {
          ...SAMPLE_ANALYSIS.finding_summary,
          sorted_findings: [],
        },
        extracted_evidence: {
          sender_domain: "",
          subject: "",
          urls: [],
          attachment_filenames: [],
          authentication_results: {
            spf_result: "unknown",
            dkim_result: "",
            dmarc_result: "unknown",
          },
        },
      },
      selectedFileName: "empty-evidence.eml",
    });

    expect(report).toContain("- Sender domain: Not available");
    expect(report).toContain("- Subject: Not available");
    expect(report).toContain("- No URLs extracted");
    expect(report).toContain("- No attachments extracted");
    expect(report).toContain("- DKIM: Not available");
    expect(report).toContain("- No findings returned by the backend.");
    expect(report).toContain("- No findings");
  });
});
