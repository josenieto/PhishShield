import { afterEach, describe, expect, it, vi } from "vitest";

import { copyMarkdownReport } from "../../src/report/copyMarkdownReport";


const SAMPLE_ANALYSIS = {
  finding_codes: ["DOMAIN_CONTAINS_PUNYCODE"],
  unique_finding_codes: ["DOMAIN_CONTAINS_PUNYCODE"],
  finding_summary: {
    findings: [
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
    ],
    finding_counts_by_category: {
      DOMAIN: 1,
    },
    highest_severity: "HIGH",
    total_findings: 1,
  },
  risk_score: {
    indicators: ["DOMAIN_CONTAINS_PUNYCODE"],
    raw_score: 30,
    capped_score: 30,
    risk_level: "MEDIUM",
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


afterEach(() => {
  vi.restoreAllMocks();
});


describe("copyMarkdownReport", () => {
  it("should write the generated Markdown report to the clipboard", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);

    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: { writeText },
    });

    await copyMarkdownReport({
      analysis: SAMPLE_ANALYSIS,
      selectedFileName: "security-review.eml",
    });

    expect(writeText).toHaveBeenCalledTimes(1);
    expect(writeText.mock.calls[0]?.[0]).toContain("# PhishShield Analysis Report");
    expect(writeText.mock.calls[0]?.[0]).toContain("- File: security\\-review.eml");
  });
});
