import type { AnalyzeEmailModelAssessmentResponse } from "../types/api";


type ModelAssessmentPanelProps = {
  modelAssessment: AnalyzeEmailModelAssessmentResponse | null;
  isAssessingModel: boolean;
  errorMessage: string;
  canAssess: boolean;
  onAssess: () => void;
};


export function ModelAssessmentPanel({
  modelAssessment,
  isAssessingModel,
  errorMessage,
  canAssess,
  onAssess,
}: ModelAssessmentPanelProps) {
  const status = modelAssessment?.model_assessment.status ?? "idle";

  return (
    <section className="findings-panel model-assessment-panel" aria-label="Model-assisted assessment">
      <div className="panel-heading">
        <h2>Model-assisted assessment</h2>
        <p>Advisory only. Does not replace deterministic findings.</p>
      </div>

      <div className="model-assessment-actions">
        <button type="button" onClick={onAssess} disabled={!canAssess || isAssessingModel}>
          {isAssessingModel ? "Assessing with model..." : "Assess with model"}
        </button>
      </div>

      {errorMessage && <p className="error-banner">{errorMessage}</p>}

      {!errorMessage && status === "idle" && (
        <p className="muted-copy">Run the separate model assessment endpoint to compare an advisory model view of the current email.</p>
      )}

      {!errorMessage && status === "not_configured" && (
        <div className="model-assessment-state">
          <strong>Model assessment is not configured yet.</strong>
          <p className="muted-copy">The endpoint is available, but no real inference backend has been enabled yet.</p>
        </div>
      )}

      {!errorMessage && status !== "idle" && status !== "not_configured" && modelAssessment && (
        <div className="model-assessment-state">
          <p><strong>Status:</strong> {modelAssessment.model_assessment.status}</p>
          <p><strong>Label:</strong> {modelAssessment.model_assessment.label}</p>
          <p><strong>Confidence:</strong> {modelAssessment.model_assessment.confidence ?? "Not available"}</p>
          <p><strong>Summary:</strong> {modelAssessment.model_assessment.summary || "Not available"}</p>
          <p><strong>Signals:</strong> {modelAssessment.model_assessment.signals.length === 0 ? "No model signals" : modelAssessment.model_assessment.signals.join(", ")}</p>
          <p><strong>Model:</strong> {modelAssessment.model_assessment.model_name || "Not available"}</p>
          <p><strong>Version:</strong> {modelAssessment.model_assessment.model_version || "Not available"}</p>
          <p><strong>Error:</strong> {modelAssessment.model_assessment.error_message || "None"}</p>
        </div>
      )}
    </section>
  );
}
