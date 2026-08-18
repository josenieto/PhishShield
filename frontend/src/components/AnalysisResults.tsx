import { useState } from "react";

import type { AnalyzeEmailResponse } from "../types/api";
import { copyMarkdownReport } from "../report/copyMarkdownReport";
import { createMarkdownReport } from "../report/createMarkdownReport";
import { downloadHtmlReport } from "../report/downloadHtmlReport";
import { downloadJsonReport } from "../report/downloadJsonReport";
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
  const [isPreviewVisible, setIsPreviewVisible] = useState(false);
  const markdownPreview = createMarkdownReport({ analysis, selectedFileName });

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
      <div className="success-banner" role="status" aria-live="polite" aria-label="Analysis completed">
        <strong>Analysis completed</strong>
        <span>
          Review the local triage output for <code>{selectedFileName}</code>.
        </span>
      </div>

      <div className="analysis-overview-grid">
        <RiskSummary analysis={analysis} />

        <section className="findings-panel report-actions-panel">
          <div className="panel-heading">
            <h2>Report actions</h2>
            <p>Reuse the current analysis as Markdown, JSON, or HTML without rerunning the backend flow.</p>
          </div>

          <div className="report-actions-grid">
            <button
              type="button"
              className="secondary-action-button"
              onClick={() => {
                setIsPreviewVisible((currentValue) => !currentValue);
              }}
            >
              {isPreviewVisible ? "Hide Markdown preview" : "Preview Markdown report"}
            </button>
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
            <button
              type="button"
              className="secondary-action-button"
              onClick={() => {
                downloadJsonReport({ analysis, selectedFileName });
              }}
            >
              Download JSON
            </button>
            <button
              type="button"
              className="secondary-action-button"
              onClick={() => {
                downloadHtmlReport({ analysis, selectedFileName });
              }}
            >
              Download HTML
            </button>
          </div>

          {copyStatusMessage && <span className="copy-report-status" role="status" aria-live="polite">{copyStatusMessage}</span>}
        </section>
      </div>

      {isPreviewVisible && (
        <section className="findings-panel report-preview-section" aria-label="Markdown report preview">
          <div className="panel-heading">
            <h2>Markdown report preview</h2>
            <p>Preview the generated report content before copying or downloading it.</p>
          </div>
          <pre className="report-preview-panel">{markdownPreview}</pre>
        </section>
      )}

      <div className="analysis-secondary-grid">
        <ExtractedEvidence extractedEvidence={analysis.extracted_evidence} />
        <IndicatorDistribution analysis={analysis} />
      </div>
      <FindingsByCategory analysis={analysis} />
      <IndicatorCodes findingCodes={analysis.unique_finding_codes} />
    </section>
  );
}
