import { describe, expect, it } from "vitest";

import { createHtmlReport } from "../../src/report/createHtmlReport";


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


describe("createHtmlReport", () => {
  it("should include the main HTML report sections and values", () => {
    const report = createHtmlReport({
      analysis: SAMPLE_ANALYSIS,
      selectedFileName: "security-review.eml",
    });

    expect(report).toContain("<!doctype html>");
    expect(report).toContain("<h1>PhishShield Analysis Report</h1>");
    expect(report).toContain("<li>File: security-review.eml</li>");
    expect(report).toContain("<li>Risk level: MEDIUM</li>");
    expect(report).toContain("<h2>Extracted Evidence</h2>");
    expect(report).toContain("<li>SPF: fail</li>");
    expect(report).toContain("<h2>Findings By Category</h2>");
    expect(report).toContain("<h3>DOMAIN</h3>");
    expect(report).toContain("<h2>Unique Indicator Codes</h2>");
  });

  it("should escape attacker-controlled values before writing HTML", () => {
    const report = createHtmlReport({
      analysis: {
        ...SAMPLE_ANALYSIS,
        unique_finding_codes: ['DOMAIN_CONTAINS_PUNYCODE<script>alert(1)</script>'],
        finding_summary: {
          ...SAMPLE_ANALYSIS.finding_summary,
          sorted_findings: [
            {
              code: 'DOMAIN_CONTAINS_PUNYCODE<script>alert(1)</script>',
              category: 'DOMAIN<img src=x onerror=alert(1)>',
              severity: "HIGH",
              explanation: 'Review <b>now</b>',
            },
          ],
        },
        extracted_evidence: {
          sender_domain: 'example.zip<script>alert(1)</script>',
          subject: 'Invoice <strong>update</strong>',
          urls: ['https://example.com/login?a=<test>'],
          attachment_filenames: ['invoice<script>.pdf'],
          authentication_results: {
            spf_result: 'fail<script>',
            dkim_result: 'pass',
            dmarc_result: 'fail',
          },
        },
      },
      selectedFileName: 'security-review.eml<script>alert(1)</script>',
    });

    expect(report).toContain("security-review.eml&lt;script&gt;alert(1)&lt;/script&gt;");
    expect(report).toContain("example.zip&lt;script&gt;alert(1)&lt;/script&gt;");
    expect(report).toContain("Invoice &lt;strong&gt;update&lt;/strong&gt;");
    expect(report).toContain("https://example.com/login?a=&lt;test&gt;");
    expect(report).toContain("invoice&lt;script&gt;.pdf");
    expect(report).toContain("fail&lt;script&gt;");
    expect(report).not.toContain("<script>alert(1)</script>");
    expect(report).not.toContain("<strong>update</strong>");
    expect(report).not.toContain("<img src=x onerror=alert(1)>");
  });
});
