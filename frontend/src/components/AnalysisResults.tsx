import type { AnalyzeEmailResponse } from "../types/api";
import { ExtractedEvidence } from "./analysis-results/ExtractedEvidence";
import { FindingsByCategory } from "./analysis-results/FindingsByCategory";
import { IndicatorCodes } from "./analysis-results/IndicatorCodes";
import { IndicatorDistribution } from "./analysis-results/IndicatorDistribution";
import { RiskSummary } from "./analysis-results/RiskSummary";


type AnalysisResultsProps = {
  analysis: AnalyzeEmailResponse;
  selectedFileName: string;
};


export function AnalysisResults({ analysis, selectedFileName }: AnalysisResultsProps) {
  return (
    <section className="analysis-panel" aria-label="Analysis results">
      <div className="success-banner">
        <strong>Analysis completed</strong>
        <span>
          Review the local triage output for <code>{selectedFileName}</code>.
        </span>
      </div>

      <RiskSummary analysis={analysis} />
      <ExtractedEvidence extractedEvidence={analysis.extracted_evidence} />
      <IndicatorDistribution analysis={analysis} />
      <FindingsByCategory analysis={analysis} />
      <IndicatorCodes findingCodes={analysis.unique_finding_codes} />
    </section>
  );
}
