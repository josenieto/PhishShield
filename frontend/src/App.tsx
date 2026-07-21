import { useEffect, useRef, useState, type FormEvent } from "react";

import { analyzeEmail } from "./api/analyzeEmail";
import { analyzeEmailModelAssessment } from "./api/analyzeEmailModelAssessment";
import { AnalysisResults } from "./components/AnalysisResults";
import { ModelAssessmentPanel } from "./components/ModelAssessmentPanel";
import type { AnalyzeEmailModelAssessmentResponse, AnalyzeEmailResponse } from "./types/api";


const FILE_INPUT_ACCEPT = ".eml,message/rfc822";


function isSupportedEmailFile(file: File): boolean {
  const normalizedName = file.name.trim().toLowerCase();
  return normalizedName.endsWith(".eml");
}


export default function App() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<AnalyzeEmailResponse | null>(null);
  const [modelAssessment, setModelAssessment] = useState<AnalyzeEmailModelAssessmentResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isAssessingModel, setIsAssessingModel] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [modelAssessmentErrorMessage, setModelAssessmentErrorMessage] = useState("");

  useEffect(() => {
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }, []);

  function clearFileInput(): void {
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  function handleSelectedFile(file: File | null): void {
    if (file === null) {
      setSelectedFile(null);
      setErrorMessage("");
      setModelAssessment(null);
      setModelAssessmentErrorMessage("");
      clearFileInput();
      return;
    }

    if (!isSupportedEmailFile(file)) {
      setSelectedFile(null);
      setAnalysis(null);
      setModelAssessment(null);
      setModelAssessmentErrorMessage("");
      setErrorMessage("Only .eml files are supported in the current frontend MVP.");
      clearFileInput();
      return;
    }

    setSelectedFile(file);
    setErrorMessage("");
    setModelAssessment(null);
    setModelAssessmentErrorMessage("");
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

  async function handleModelAssessment(): Promise<void> {
    if (selectedFile === null) {
      setModelAssessmentErrorMessage("Choose an .eml file before requesting model assessment.");
      return;
    }

    setIsAssessingModel(true);
    setModelAssessmentErrorMessage("");

    try {
      const result = await analyzeEmailModelAssessment(selectedFile);
      setModelAssessment(result);
    } catch (error) {
      setModelAssessment(null);
      setModelAssessmentErrorMessage(
        error instanceof Error ? error.message : "Unexpected model assessment error.",
      );
    } finally {
      setIsAssessingModel(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="workbench-shell">
        <header className="hero-card workbench-hero">
          <div>
            <p className="eyebrow">PhishShield</p>
            <h1>Local email triage workbench</h1>
          </div>
          <p className="lede workbench-lede">
            Upload an <code>.eml</code> message and inspect the local backend risk posture,
            grouped indicators, and current evidence summary.
          </p>
        </header>

        <div className="workbench-grid">
          <aside className="workbench-sidebar">
            <section className="hero-card sidebar-card">
              <div className="sidebar-card-heading">
                <h2>Analysis input</h2>
                <p>Load a local email and send it to the current backend triage flow.</p>
              </div>

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
                    ref={fileInputRef}
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
            </section>

            <div className="status-grid sidebar-status-grid">
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
          </aside>

          <section className="workbench-main">
            {isAnalyzing && (
              <section className="empty-state-panel empty-state-panel-main">
                <h2>Analysis in progress</h2>
                <p>
                  The selected email is being submitted to the local backend for risk scoring
                  and indicator triage.
                </p>
              </section>
            )}

            {analysis === null && !errorMessage && !isAnalyzing && (
              <section className="empty-state-panel empty-state-panel-main">
                <h2>No analysis loaded</h2>
                <p>
                  Upload an <code>.eml</code> file to render the current backend findings,
                  risk score, and grouped indicators.
                </p>
              </section>
            )}

            {analysis && (
              <>
                <AnalysisResults
                  analysis={analysis}
                  selectedFileName={selectedFile?.name ?? "selected-email.eml"}
                />
                <ModelAssessmentPanel
                  modelAssessment={modelAssessment}
                  isAssessingModel={isAssessingModel}
                  errorMessage={modelAssessmentErrorMessage}
                  canAssess={selectedFile !== null}
                  onAssess={() => {
                    void handleModelAssessment();
                  }}
                />
              </>
            )}
          </section>
        </div>
      </section>
    </main>
  );
}
