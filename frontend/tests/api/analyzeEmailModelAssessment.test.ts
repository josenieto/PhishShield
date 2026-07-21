import { afterEach, describe, expect, it, vi } from "vitest";

import { analyzeEmailModelAssessment } from "../../src/api/analyzeEmailModelAssessment";


const SAMPLE_FILE = new File(["sample"], "sample.eml", {
  type: "message/rfc822",
});


afterEach(() => {
  vi.restoreAllMocks();
});


describe("analyzeEmailModelAssessment", () => {
  it("should return parsed model assessment payload on success", async () => {
    const payload = {
      model_assessment: {
        status: "not_configured",
        label: "unknown",
        confidence: null,
        summary: "",
        signals: [],
        model_name: "",
        model_version: "",
        error_message: "",
      },
    };

    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify(payload), { status: 200 }),
    );

    await expect(analyzeEmailModelAssessment(SAMPLE_FILE)).resolves.toEqual(payload);
    expect(fetchSpy).toHaveBeenCalledWith(
      "/api/analyze-email-model-assessment",
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

    await expect(analyzeEmailModelAssessment(SAMPLE_FILE)).rejects.toThrow(
      "The selected email exceeds the configured upload limit.",
    );
  });

  it("should return the backend detail for model assessment failures", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({ detail: "Uploaded email could not be assessed by the model." }),
        { status: 422 },
      ),
    );

    await expect(analyzeEmailModelAssessment(SAMPLE_FILE)).rejects.toThrow(
      "Uploaded email could not be assessed by the model.",
    );
  });

  it("should return a connectivity message when the backend is unreachable", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("fetch failed"));

    await expect(analyzeEmailModelAssessment(SAMPLE_FILE)).rejects.toThrow(
      "The backend is not reachable. Start the API and try again.",
    );
  });
});
