import type { AnalyzeEmailResponse } from "../../types/api";

import { formatRiskScore, formatRiskScoreDetails } from "../../formatRiskScore";
import { riskPostureHint } from "./shared";


type RiskSummaryProps = {
  analysis: AnalyzeEmailResponse;
};


export function RiskSummary({ analysis }: RiskSummaryProps) {
  return (
    <section
      className={`findings-panel findings-panel-spotlight risk-summary risk-summary-${analysis.risk_score.risk_level.toLowerCase()}`}
      aria-label="Risk assessment"
    >
      <div className="panel-heading panel-heading-inline">
        <div>
          <h2>Risk assessment</h2>
          <p>{riskPostureHint(analysis)}</p>
        </div>
        <span
          className={`risk-level-pill risk-level-${analysis.risk_score.risk_level.toLowerCase()}`}
          aria-label={`Risk level ${analysis.risk_score.risk_level}`}
        >
          {analysis.risk_score.risk_level}
        </span>
      </div>

      <div className="analysis-summary-grid">
        <article className="summary-card summary-card-accent summary-card-priority">
          <span className="summary-label">Risk posture</span>
          <strong className="summary-metric">{analysis.risk_score.risk_level}</strong>
          <span className="summary-subtext">
            {formatRiskScore(analysis.risk_score)}
          </span>
          <span className="summary-subtext">
            {formatRiskScoreDetails(analysis.risk_score)}
          </span>
        </article>

        <article className={`summary-card critical-indicator-card${analysis.risk_score.has_critical_indicators ? " critical-indicator-card-active" : ""}`}>
          <span className="summary-label">Critical indicators</span>
          <strong className="summary-metric-compact">
            {analysis.risk_score.has_critical_indicators ? "Present" : "Not observed"}
          </strong>
          <span className="summary-subtext">
            {analysis.risk_score.has_critical_indicators
              ? "Review these findings before the remaining evidence."
              : `Highest severity reported: ${analysis.finding_summary.highest_severity}.`}
          </span>
        </article>

        <article className="summary-card">
          <span className="summary-label">Indicator volume</span>
          <strong className="summary-metric-compact">{analysis.finding_summary.total_findings}</strong>
          <span className="summary-subtext">
            {analysis.unique_finding_codes.length} unique codes across the analyzed message.
          </span>
        </article>
      </div>
    </section>
  );
}
