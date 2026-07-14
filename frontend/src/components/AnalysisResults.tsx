import type { AnalyzeEmailResponse } from "../types/api";


function severityClassName(severity: string): string {
  return `severity-badge severity-${severity.toLowerCase()}`;
}


function groupFindingsByCategory(analysis: AnalyzeEmailResponse) {
  const groupedFindings = new Map<string, AnalyzeEmailResponse["finding_summary"]["sorted_findings"]>();

  for (const finding of analysis.finding_summary.sorted_findings) {
    const currentFindings = groupedFindings.get(finding.category) ?? [];
    currentFindings.push(finding);
    groupedFindings.set(finding.category, currentFindings);
  }

  return Array.from(groupedFindings.entries());
}


function sortedCategoryCounts(analysis: AnalyzeEmailResponse): Array<[string, number]> {
  return Object.entries(analysis.finding_summary.finding_counts_by_category).sort((left, right) => {
    if (right[1] !== left[1]) {
      return right[1] - left[1];
    }

    return left[0].localeCompare(right[0]);
  });
}


function displayValue(value: string): string {
  return value.trim() === "" ? "Not available" : value;
}


type AnalysisResultsProps = {
  analysis: AnalyzeEmailResponse;
  selectedFileName: string;
};


export function AnalysisResults({ analysis, selectedFileName }: AnalysisResultsProps) {
  const categoryCounts = sortedCategoryCounts(analysis);
  const extractedEvidence = analysis.extracted_evidence;

  return (
    <section className="analysis-panel" aria-label="Analysis results">
      <div className="success-banner">
        <strong>Analysis completed</strong>
        <span>
          Review the local triage output for <code>{selectedFileName}</code>.
        </span>
      </div>

      <div className="analysis-summary-grid">
        <article className="summary-card summary-card-accent">
          <span className="summary-label">Risk posture</span>
          <strong>{analysis.risk_score.risk_level}</strong>
          <span className="summary-subtext">
            Raw score {analysis.risk_score.raw_score}, capped at {analysis.risk_score.capped_score}.
          </span>
        </article>

        <article className="summary-card">
          <span className="summary-label">Critical indicators</span>
          <strong>
            {analysis.risk_score.has_critical_indicators ? "Present" : "Not observed"}
          </strong>
          <span className="summary-subtext">
            Highest severity reported: {analysis.finding_summary.highest_severity}.
          </span>
        </article>

        <article className="summary-card">
          <span className="summary-label">Indicator volume</span>
          <strong>{analysis.finding_summary.total_findings}</strong>
          <span className="summary-subtext">
            {analysis.unique_finding_codes.length} unique codes across the analyzed message.
          </span>
        </article>
      </div>

      <section className="findings-panel">
        <div className="panel-heading">
          <h2>Extracted evidence</h2>
          <p>Normalized message details extracted by the backend before indicator analysis.</p>
        </div>

        <div className="evidence-grid">
          <article className="evidence-card">
            <span className="summary-label">Sender domain</span>
            <strong>{displayValue(extractedEvidence.sender_domain)}</strong>
          </article>

          <article className="evidence-card evidence-card-wide">
            <span className="summary-label">Subject</span>
            <strong>{displayValue(extractedEvidence.subject)}</strong>
          </article>

          <article className="evidence-card evidence-card-wide">
            <span className="summary-label">URLs</span>
            {extractedEvidence.urls.length === 0 ? (
              <p className="muted-copy">No URLs extracted</p>
            ) : (
              <ul className="evidence-list">
                {extractedEvidence.urls.map((url) => (
                  <li key={url} className="evidence-list-item">
                    <code>{url}</code>
                  </li>
                ))}
              </ul>
            )}
          </article>

          <article className="evidence-card">
            <span className="summary-label">Attachments</span>
            {extractedEvidence.attachment_filenames.length === 0 ? (
              <p className="muted-copy">No attachments extracted</p>
            ) : (
              <ul className="evidence-list">
                {extractedEvidence.attachment_filenames.map((filename) => (
                  <li key={filename} className="evidence-list-item">
                    <code>{filename}</code>
                  </li>
                ))}
              </ul>
            )}
          </article>

          <article className="evidence-card evidence-card-wide">
            <span className="summary-label">Authentication results</span>
            <dl className="auth-grid">
              <div className="auth-item">
                <dt>SPF</dt>
                <dd>{displayValue(extractedEvidence.authentication_results.spf_result)}</dd>
              </div>
              <div className="auth-item">
                <dt>DKIM</dt>
                <dd>{displayValue(extractedEvidence.authentication_results.dkim_result)}</dd>
              </div>
              <div className="auth-item">
                <dt>DMARC</dt>
                <dd>{displayValue(extractedEvidence.authentication_results.dmarc_result)}</dd>
              </div>
            </dl>
          </article>
        </div>
      </section>

      <section className="findings-panel">
        <div className="panel-heading">
          <h2>Evidence overview</h2>
          <p>Category counts help show where the strongest signals are concentrated.</p>
        </div>

        {categoryCounts.length === 0 ? (
          <p className="muted-copy">No category evidence was returned by the backend.</p>
        ) : (
          <div className="category-overview-grid">
            {categoryCounts.map(([category, count]) => (
              <article key={category} className="category-overview-card">
                <span className="summary-label">{category}</span>
                <strong>{count}</strong>
                <span className="summary-subtext">
                  {count === 1 ? "indicator" : "indicators"}
                </span>
              </article>
            ))}
          </div>
        )}
      </section>

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
                    <div>
                      <strong>{finding.code}</strong>
                      <p>{finding.category} signal</p>
                    </div>
                    <span className={severityClassName(finding.severity)}>{finding.severity}</span>
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      </section>

      <section className="findings-panel">
        <div className="panel-heading">
          <h2>Indicator codes</h2>
          <p>Unique finding codes returned by the backend for the selected message.</p>
        </div>

        <div className="indicator-chip-grid">
          {analysis.unique_finding_codes.length === 0 ? (
            <span className="indicator-chip indicator-chip-safe">No findings</span>
          ) : (
            analysis.unique_finding_codes.map((findingCode) => (
              <span key={findingCode} className="indicator-chip">
                {findingCode}
              </span>
            ))
          )}
        </div>
      </section>
    </section>
  );
}
