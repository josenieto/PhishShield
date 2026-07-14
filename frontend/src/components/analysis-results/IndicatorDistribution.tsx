import type { AnalyzeEmailResponse } from "../../types/api";

import { sortedCategoryCounts } from "./shared";


type IndicatorDistributionProps = {
  analysis: AnalyzeEmailResponse;
};


export function IndicatorDistribution({ analysis }: IndicatorDistributionProps) {
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
          {categoryCounts.map(([category, count]) => (
            <article key={category} className="category-overview-card">
              <span className="summary-label">{category}</span>
              <strong>{count}</strong>
              <span className="summary-subtext">{count === 1 ? "indicator" : "indicators"}</span>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
