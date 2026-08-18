import { describe, expect, it } from "vitest";

import { formatRiskScore, formatRiskScoreDetails } from "../src/formatRiskScore";


describe("formatRiskScore", () => {
  it("always presents the capped score on the 100-point scale", () => {
    expect(formatRiskScore({ raw_score: 30, capped_score: 30 })).toBe("Score: 30/100");
  });

  it("explains when the raw score was capped", () => {
    expect(formatRiskScore({ raw_score: 135, capped_score: 100 })).toBe("Score: 100/100");
    expect(formatRiskScoreDetails({ raw_score: 135, capped_score: 100 })).toBe("Raw score: 135 (capped at 100)");
  });

  it("does not imply capping when raw and capped scores match", () => {
    expect(formatRiskScoreDetails({ raw_score: 30, capped_score: 30 })).toBe("Raw score: 30");
  });
});
