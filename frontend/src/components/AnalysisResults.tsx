import { useState } from "react";

import type { AnalyzeEmailResponse } from "../types/api";
import { copyMarkdownReport } from "../report/copyMarkdownReport";
import { ExtractedEvidence } from "./analysis-results/ExtractedEvidence";
import { FindingsByCategory } from "./analysis-results/FindingsByCategory";
import { IndicatorCodes } from "./analysis-results/IndicatorCodes";
import { IndicatorDistribution } from "./analysis-results/IndicatorDistribution";
import { RiskSummary } from "./analysis-results/RiskSummary";
import { downloadMarkdownReport } from "../report/downloadMarkdownReport";


type AnalysisResultsProps = {
  analysis: AnalyzeEmailResponse;
  selectedFileName: string;
};


export function AnalysisResults({ analysis, selectedFileName }: AnalysisResultsProps) {
  const [copyStatusMessage, setCopyStatusMessage] = useState("");

  async function handleCopyReport(): Promise<void> {
    try {
      await copyMarkdownReport({ analysis, selectedFileName });
      setCopyStatusMessage("Markdown report copied");
    } catch {
      setCopyStatusMessage("Markdown report could not be copied");
    }
  }

  return (
    <section className="analysis-panel" aria-label="Analysis results">
      <div className="success-banner">
        <strong>Analysis completed</strong>
        <span>
          Review the local triage output for <code>{selectedFileName}</code>.
        </span>
        <div className="success-banner-actions">
          <button
            type="button"
            className="secondary-action-button"
            onClick={() => {
              void handleCopyReport();
            }}
          >
            Copy Markdown report
          </button>
          <button
            type="button"
            className="secondary-action-button"
            onClick={() => {
              downloadMarkdownReport({ analysis, selectedFileName });
            }}
          >
            Download Markdown report
          </button>
        </div>
        {copyStatusMessage && <span className="copy-report-status">{copyStatusMessage}</span>}
      </div>

      <RiskSummary analysis={analysis} />
      <div className="analysis-secondary-grid">
        <ExtractedEvidence extractedEvidence={analysis.extracted_evidence} />
        <IndicatorDistribution analysis={analysis} />
      </div>
      <FindingsByCategory analysis={analysis} />
      <IndicatorCodes findingCodes={analysis.unique_finding_codes} />
    </section>
  );
}
