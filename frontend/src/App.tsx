import { useEffect, useRef, useState, type DragEvent, type FormEvent } from "react";

import { analyzeEmail } from "./api/analyzeEmail";
import { analyzeEmailModelAssessment } from "./api/analyzeEmailModelAssessment";
import { AnalysisResults } from "./components/AnalysisResults";
import { ModelAssessmentPanel } from "./components/ModelAssessmentPanel";
import { getDroppedFile } from "./fileSelection";
import type { AnalyzeEmailModelAssessmentResponse, AnalyzeEmailResponse } from "./types/api";


const FILE_INPUT_ACCEPT = ".eml,message/rfc822";


function isSupportedEmailFile(file: File): boolean {
  const normalizedName = file.name.trim().toLowerCase();
  return normalizedName.endsWith(".eml");
}


export default function App() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const dragDepthRef = useRef(0);
  const requestSequenceRef = useRef(0);
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
    if (isAnalyzing || isAssessingModel) {
      return;
    }

    requestSequenceRef.current += 1;

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

  function handleDragEnter(event: DragEvent<HTMLFormElement>): void {
    event.preventDefault();
    if (isAnalyzing || isAssessingModel) {
      return;
    }

    dragDepthRef.current += 1;
    setIsDragOver(true);
    event.dataTransfer.dropEffect = "copy";
  }

  function handleDragOver(event: DragEvent<HTMLFormElement>): void {
    event.preventDefault();
    if (!isAnalyzing && !isAssessingModel) {
      event.dataTransfer.dropEffect = "copy";
    }
  }

  function handleDragLeave(event: DragEvent<HTMLFormElement>): void {
    event.preventDefault();
    dragDepthRef.current = Math.max(0, dragDepthRef.current - 1);
    if (dragDepthRef.current === 0) {
      setIsDragOver(false);
    }
  }

  function handleDrop(event: DragEvent<HTMLFormElement>): void {
    event.preventDefault();
    dragDepthRef.current = 0;
    setIsDragOver(false);
    if (isAnalyzing || isAssessingModel) {
      return;
    }

    handleSelectedFile(getDroppedFile(event.dataTransfer));
  }

  async function handleAnalyzeSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (selectedFile === null) {
      setErrorMessage("Choose an .eml file before starting the analysis.");
      return;
    }

    const fileToAnalyze = selectedFile;
    const requestSequence = ++requestSequenceRef.current;
    setIsAnalyzing(true);
    setErrorMessage("");
    setAnalysis(null);
    setModelAssessment(null);
    setModelAssessmentErrorMessage("");

    try {
      const result = await analyzeEmail(fileToAnalyze);
      if (requestSequence === requestSequenceRef.current) {
        setAnalysis(result);
      }
    } catch (error) {
      if (requestSequence === requestSequenceRef.current) {
        setAnalysis(null);
        setErrorMessage(
          error instanceof Error ? error.message : "Unexpected analysis error.",
        );
      }
    } finally {
      if (requestSequence === requestSequenceRef.current) {
        setIsAnalyzing(false);
      }
    }
  }

  async function handleModelAssessment(): Promise<void> {
    if (selectedFile === null) {
      setModelAssessmentErrorMessage("Choose an .eml file before requesting model assessment.");
      return;
    }

    const fileToAssess = selectedFile;
    const requestSequence = ++requestSequenceRef.current;
    setIsAssessingModel(true);
    setModelAssessmentErrorMessage("");

    try {
      const result = await analyzeEmailModelAssessment(fileToAssess);
      if (requestSequence === requestSequenceRef.current) {
        setModelAssessment(result);
      }
    } catch (error) {
      if (requestSequence === requestSequenceRef.current) {
        setModelAssessment(null);
        setModelAssessmentErrorMessage(
          error instanceof Error ? error.message : "Unexpected model assessment error.",
        );
      }
    } finally {
      if (requestSequence === requestSequenceRef.current) {
        setIsAssessingModel(false);
      }
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

        <div className={`workbench-grid${analysis ? " workbench-grid-analysis-ready" : ""}`}>
          <aside className="workbench-sidebar">
            <section className="hero-card sidebar-card">
              <div className="sidebar-card-heading">
                <h2>Analysis input</h2>
                <p>Load a local email and send it to the current backend triage flow.</p>
              </div>

                <form
                  className={`upload-panel ${isDragOver ? "upload-panel-dragover" : ""}`}
                  aria-label="Email upload"
                  onSubmit={handleAnalyzeSubmit}
                  onDragEnter={handleDragEnter}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                >
                  <label
                    className={`file-input-card ${isDragOver ? "file-input-card-dragover" : ""}`}
                    htmlFor="email-file"
                  >
                  <span className="file-input-title">Email file</span>
                  <span className="file-input-help">
                    Choose or drag a <code>.eml</code> message to send to <code>/api/analyze-email</code>.
                  </span>
                  <span className="file-input-status" aria-live="polite">
                    {selectedFile ? `Selected: ${selectedFile.name}` : "No file selected"}
                  </span>
                  <span id="privacy-notice" className="file-input-help">
                    Privacy: This deployment processes email through the configured backend.
                    Use a trusted local or internal deployment for confidential email. Do not
                    upload confidential or production email to a public or untrusted host.
                  </span>
                    <span className="file-input-button">Choose .eml file</span>
                    <input
                      ref={fileInputRef}
                      id="email-file"
                      className="visually-hidden-file-input"
                      type="file"
                      accept={FILE_INPUT_ACCEPT}
                      aria-describedby="privacy-notice"
                      disabled={isAnalyzing || isAssessingModel}
                     onChange={(event) => {
                       handleSelectedFile(event.target.files?.[0] ?? null);
                     }}
                   />
                </label>

                 <div className="upload-actions">
                  <button type="submit" disabled={isAnalyzing || isAssessingModel || selectedFile === null}>
                    {isAnalyzing ? "Analyzing local email..." : "Analyze email"}
                  </button>
                </div>
              </form>

              {errorMessage && <p className="error-banner" role="alert">{errorMessage}</p>}
            </section>

            <div className="status-grid sidebar-status-grid">
              <article>
                <h2>Execution path</h2>
                <p>
                  Browser upload to <code>/api/analyze-email</code>, proxied to the local
                   FastAPI service through the frontend proxy.
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

          <section className="workbench-main" aria-busy={isAnalyzing || isAssessingModel}>
            {isAnalyzing && (
              <section className="empty-state-panel empty-state-panel-main" role="status" aria-live="polite">
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
                   canAssess={selectedFile !== null && !isAnalyzing && !isAssessingModel}
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
