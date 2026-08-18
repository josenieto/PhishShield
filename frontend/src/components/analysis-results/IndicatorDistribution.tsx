import type { AnalyzeEmailResponse } from "../../types/api";

import { groupFindingsByCategory, highestSeverity, severityToneClass, sortedCategoryCounts } from "./shared";


type IndicatorDistributionProps = {
  analysis: AnalyzeEmailResponse;
};


export function IndicatorDistribution({ analysis }: IndicatorDistributionProps) {
  const categoryFindings = groupFindingsByCategory(analysis);
  const findingsByCategory = new Map(categoryFindings);
  const categoryCounts = sortedCategoryCounts(analysis);

  return (
    <section className="findings-panel">
      <div className="panel-heading">
        <h2>Indicator distribution</h2>
        <p>Category counts show where the strongest clusters of evidence are concentrated.</p>
      </div>

      {categoryCounts.length === 0 ? (
        <p className="muted-copy">No category evidence was returned by the backend.</p>
      ) : (
        <div className="category-overview-grid">
          {categoryCounts.map(([category, count]) => {
            const findings = findingsByCategory.get(category) ?? [];
            const severity = findings.length === 0 ? "UNKNOWN" : highestSeverity(findings);

            return (
            <article key={category} className={`category-overview-card ${severityToneClass(severity)}`}>
              <span className="summary-label">{category}</span>
              <strong>{count}</strong>
              <span className="summary-subtext">{count === 1 ? "indicator" : "indicators"}</span>
              <span className="category-overview-severity">Highest severity: {severity}</span>
            </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
