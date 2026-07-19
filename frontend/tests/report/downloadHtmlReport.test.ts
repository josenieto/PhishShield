import { afterEach, describe, expect, it, vi } from "vitest";

import { downloadHtmlReport } from "../../src/report/downloadHtmlReport";


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


describe("downloadHtmlReport", () => {
  it("should create an HTML object URL, set the download name, click the anchor, and revoke the URL", () => {
    const clickSpy = vi.fn();
    const anchor = document.createElement("a");
    anchor.click = clickSpy;
    const originalCreateElement = document.createElement.bind(document);
    const blobParts: BlobPart[] = [];
    const blobType = { value: "" };
    const createObjectURL = vi.fn().mockReturnValue("blob:test-html-url");
    const revokeObjectURL = vi.fn();

    const BlobConstructor = vi.fn().mockImplementation((parts: BlobPart[], options?: BlobPropertyBag) => {
      blobParts.push(...parts);
      blobType.value = options?.type ?? "";

      return {};
    });

    Object.defineProperty(URL, "createObjectURL", {
      configurable: true,
      writable: true,
      value: createObjectURL,
    });
    Object.defineProperty(URL, "revokeObjectURL", {
      configurable: true,
      writable: true,
      value: revokeObjectURL,
    });
    vi.stubGlobal("Blob", BlobConstructor);

    const createElementSpy = vi.spyOn(document, "createElement").mockImplementation((tagName: string) => {
      if (tagName === "a") {
        return anchor;
      }

      return originalCreateElement(tagName);
    });

    downloadHtmlReport({
      analysis: SAMPLE_ANALYSIS,
      selectedFileName: "security review.eml",
    });

    expect(createElementSpy).toHaveBeenCalledWith("a");
    expect(createObjectURL).toHaveBeenCalledTimes(1);
    expect(BlobConstructor).toHaveBeenCalledTimes(1);
    expect(anchor.href).toBe("blob:test-html-url");
    expect(anchor.download).toBe("phishshield-report-security-review.html");
    expect(clickSpy).toHaveBeenCalledTimes(1);
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:test-html-url");
    expect(blobType.value).toBe("text/html;charset=utf-8");

    const blobContent = blobParts.join("");
    expect(blobContent).toContain("<h1>PhishShield Analysis Report</h1>");
    expect(blobContent).toContain("security review.eml");
  });
});
