import type { AnalyzeEmailResponse } from "../../types/api";

import { groupFindingsByCategory, severityClassName } from "./shared";


type FindingsByCategoryProps = {
  analysis: AnalyzeEmailResponse;
};


export function FindingsByCategory({ analysis }: FindingsByCategoryProps) {
  return (
    <section className="findings-panel">
      <div className="panel-heading">
        <h2>Findings by category</h2>
        <p>Indicators are grouped by backend category and ordered by severity inside each section.</p>
      </div>

      <div className="finding-category-grid">
        {groupFindingsByCategory(analysis).map(([category, findings]) => (
          <section key={category} className="finding-category-card">
            <div className="finding-category-header">
              <h3>{category}</h3>
              <span className="category-count-chip">{findings.length}</span>
            </div>

            <ul className="finding-list">
              {findings.map((finding) => (
                <li key={finding.code} className="finding-item">
                  <div className="finding-content">
                    <div className="finding-header-row">
                      <strong>{finding.code}</strong>
                      <span className={severityClassName(finding.severity)}>{finding.severity}</span>
                    </div>
                    <p className="finding-category-copy">Backend category: {finding.category}</p>
                    <p className="finding-explanation">{finding.explanation}</p>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </section>
  );
}
