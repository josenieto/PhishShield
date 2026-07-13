import { useState, type FormEvent } from "react";

import { analyzeEmail } from "./api/analyzeEmail";
import { AnalysisResults } from "./components/AnalysisResults";
import type { AnalyzeEmailResponse } from "./types/api";


const FILE_INPUT_ACCEPT = ".eml,message/rfc822";


function isSupportedEmailFile(file: File): boolean {
  const normalizedName = file.name.trim().toLowerCase();
  return normalizedName.endsWith(".eml");
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
      setErrorMessage("");
      return;
    }

    if (!isSupportedEmailFile(file)) {
      setSelectedFile(null);
      setAnalysis(null);
      setErrorMessage("Only .eml files are supported in the current frontend MVP.");
      return;
    }

    setSelectedFile(file);
    setErrorMessage("");
  }

  async function handleAnalyzeSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (selectedFile === null) {
      setErrorMessage("Choose an .eml file before starting the analysis.");
      return;
    }

    setIsAnalyzing(true);
    setErrorMessage("");
    setAnalysis(null);

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
        <h1>Local email triage workbench</h1>
        <p className="lede">
          Upload an <code>.eml</code> message and inspect the local backend risk posture,
          grouped indicators, and current evidence summary.
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
              Choose or drag a <code>.eml</code> message to send to <code>/api/analyze-email</code>.
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
              {isAnalyzing ? "Analyzing local email..." : "Analyze email"}
            </button>
          </div>
        </form>

        {errorMessage && <p className="error-banner">{errorMessage}</p>}

        <div className="status-grid status-grid-top">
          <article>
            <h2>Execution path</h2>
            <p>
              Browser upload to <code>/api/analyze-email</code>, proxied to the local
              FastAPI service at <code>http://127.0.0.1:8000</code>.
            </p>
          </article>
          <article>
            <h2>Current scope</h2>
            <p>
              The MVP focuses on local <code>.eml</code> triage, risk scoring, grouped
              findings, and a readable evidence summary.
            </p>
          </article>
        </div>

        {isAnalyzing && (
          <section className="empty-state-panel">
            <h2>Analysis in progress</h2>
            <p>
              The selected email is being submitted to the local backend for risk scoring
              and indicator triage.
            </p>
          </section>
        )}

        {analysis === null && !errorMessage && !isAnalyzing && (
          <section className="empty-state-panel">
            <h2>No analysis loaded</h2>
            <p>
              Upload an <code>.eml</code> file to render the current backend findings,
              risk score, and grouped indicators.
            </p>
          </section>
        )}

        {analysis && <AnalysisResults analysis={analysis} selectedFileName={selectedFile?.name ?? "selected-email.eml"} />}
      </section>
    </main>
  );
}
