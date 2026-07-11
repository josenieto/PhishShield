import { describe, expect, it, vi, afterEach } from "vitest";

import { analyzeEmail } from "./analyzeEmail";


const SAMPLE_FILE = new File(["sample"], "sample.eml", {
  type: "message/rfc822",
});


afterEach(() => {
  vi.restoreAllMocks();
});


describe("analyzeEmail", () => {
  it("should return parsed analysis payload on success", async () => {
    const payload = {
      finding_codes: [],
      unique_finding_codes: [],
      finding_summary: {
        findings: [],
        sorted_findings: [],
        finding_counts_by_category: {},
        highest_severity: "UNKNOWN",
        total_findings: 0,
      },
      risk_score: {
        indicators: [],
        raw_score: 0,
        capped_score: 0,
        risk_level: "LOW",
        has_critical_indicators: false,
      },
    };

    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify(payload), { status: 200 }),
    );

    await expect(analyzeEmail(SAMPLE_FILE)).resolves.toEqual(payload);
    expect(fetchSpy).toHaveBeenCalledWith(
      "/api/analyze-email",
      expect.objectContaining({
        method: "POST",
      }),
    );
  });

  it("should return a specific message for oversized uploads", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({ detail: "Uploaded email exceeds maximum allowed size." }),
        { status: 413 },
      ),
    );

    await expect(analyzeEmail(SAMPLE_FILE)).rejects.toThrow(
      "The selected email exceeds the configured upload limit.",
    );
  });

  it("should return the backend detail for analysis failures", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({ detail: "Uploaded email could not be analyzed." }),
        { status: 422 },
      ),
    );

    await expect(analyzeEmail(SAMPLE_FILE)).rejects.toThrow(
      "Uploaded email could not be analyzed.",
    );
  });

  it("should return a connectivity message when the backend is unreachable", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("fetch failed"));

    await expect(analyzeEmail(SAMPLE_FILE)).rejects.toThrow(
      "The backend is not reachable. Start the API and try again.",
    );
  });
});
