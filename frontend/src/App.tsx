import { useState } from "react";

import { analyzeEmail } from "./api/analyzeEmail";
import type { AnalyzeEmailResponse } from "./types/api";


const FILE_INPUT_ACCEPT = ".eml,message/rfc822";


function isSupportedEmailFile(file: File): boolean {
  const normalizedName = file.name.trim().toLowerCase();
  return normalizedName.endsWith(".eml");
}


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


export default function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<AnalyzeEmailResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  function handleSelectedFile(file: File | null): void {
    if (file === null) {
      setSelectedFile(null);
      return;
    }

    if (!isSupportedEmailFile(file)) {
      setSelectedFile(null);
      setErrorMessage("Only .eml files are supported in the current frontend MVP.");
      return;
    }

    setSelectedFile(file);
    setErrorMessage("");
  }

  async function handleAnalyzeSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (selectedFile === null) {
      setErrorMessage("Choose an .eml file before starting the analysis.");
      return;
    }

    setIsAnalyzing(true);
    setErrorMessage("");

    try {
      const result = await analyzeEmail(selectedFile);
      setAnalysis(result);
    } catch (error) {
      setAnalysis(null);
      setErrorMessage(
        error instanceof Error ? error.message : "Unexpected analysis error.",
      );
    } finally {
      setIsAnalyzing(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="hero-card">
        <p className="eyebrow">PhishShield</p>
        <h1>Email analysis frontend MVP</h1>
        <p className="lede">
          Upload an `.eml` file and inspect the current backend risk score plus
          extracted findings.
        </p>

        <form className="upload-panel" onSubmit={handleAnalyzeSubmit}>
          <label
            className={`file-input-card ${isDragOver ? "file-input-card-dragover" : ""}`}
            htmlFor="email-file"
            onDragOver={(event) => {
              event.preventDefault();
              setIsDragOver(true);
            }}
            onDragLeave={(event) => {
              event.preventDefault();
              setIsDragOver(false);
            }}
            onDrop={(event) => {
              event.preventDefault();
              setIsDragOver(false);
              handleSelectedFile(event.dataTransfer.files?.[0] ?? null);
            }}
          >
            <span className="file-input-title">Email file</span>
            <span className="file-input-help">
              Choose or drag a `.eml` message to send to `/api/analyze-email`.
            </span>
            <input
              id="email-file"
              type="file"
              accept={FILE_INPUT_ACCEPT}
              onChange={(event) => {
                handleSelectedFile(event.target.files?.[0] ?? null);
              }}
            />
          </label>

          <div className="upload-actions">
            <div className="selected-file-card">
              <span className="selected-file-label">Selected file</span>
              <strong>{selectedFile?.name ?? "No file selected yet"}</strong>
            </div>

            <button type="submit" disabled={isAnalyzing || selectedFile === null}>
              {isAnalyzing ? "Analyzing..." : "Analyze email"}
            </button>
          </div>
        </form>

        {errorMessage && <p className="error-banner">{errorMessage}</p>}

        <div className="status-grid status-grid-top">
          <article>
            <h2>Backend API</h2>
            <p>`POST /api/analyze-email` proxied to `http://127.0.0.1:8000`.</p>
          </article>
          <article>
            <h2>Next Step</h2>
            <p>Refine the UI, drag and drop, and grouped findings if this flow works.</p>
          </article>
        </div>

        {analysis && (
          <section className="analysis-panel">
            <div className="analysis-summary-grid">
              <article className="summary-card summary-card-accent">
                <span className="summary-label">Risk level</span>
                <strong>{analysis.risk_score.risk_level}</strong>
                <span className="summary-subtext">
                  Score {analysis.risk_score.raw_score} / {analysis.risk_score.capped_score}
                </span>
              </article>

              <article className="summary-card">
                <span className="summary-label">Critical indicators</span>
                <strong>
                  {analysis.risk_score.has_critical_indicators ? "Present" : "None"}
                </strong>
                <span className="summary-subtext">
                  Highest severity {analysis.finding_summary.highest_severity}
                </span>
              </article>

              <article className="summary-card">
                <span className="summary-label">Findings</span>
                <strong>{analysis.finding_summary.total_findings}</strong>
                <span className="summary-subtext">
                  {analysis.unique_finding_codes.length} unique indicators
                </span>
              </article>
            </div>

            <section className="findings-panel">
              <div className="panel-heading">
                <h2>Findings by category</h2>
                <p>Grouped by backend category and ordered by severity inside each section.</p>
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
                            <p>{finding.category}</p>
                          </div>
                          <span className={severityClassName(finding.severity)}>
                            {finding.severity}
                          </span>
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
                <p>Unique finding codes returned by the backend.</p>
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
        )}
      </section>
    </main>
  );
}
