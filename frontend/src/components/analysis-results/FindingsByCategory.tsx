import type { AnalyzeEmailResponse } from "../../types/api";

import { groupFindingsByCategory, highestSeverity, severityClassName, severityToneClass } from "./shared";


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
        {groupFindingsByCategory(analysis).map(([category, findings]) => {
          const categorySeverity = highestSeverity(findings);

          return (
          <section key={category} className={`finding-category-card ${severityToneClass(categorySeverity)}`}>
            <div className="finding-category-header">
              <div>
                <h3>{category}</h3>
                <span className="finding-category-priority">Highest severity: {categorySeverity}</span>
              </div>
              <span className="category-count-chip" aria-label={`${findings.length} findings`}>{findings.length}</span>
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
          );
        })}
      </div>
    </section>
  );
}
