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
  const assessment = modelAssessment?.model_assessment;

  return (
    <section className="findings-panel model-assessment-panel" aria-label="Model-assisted assessment">
      <div className="panel-heading">
        <h2>Model-assisted assessment</h2>
        <p>Experimental and advisory only. Does not replace deterministic findings.</p>
      </div>

      <div className="model-assessment-actions">
        <button type="button" onClick={onAssess} disabled={!canAssess || isAssessingModel}>
          {isAssessingModel ? "Assessing with model..." : "Assess with model"}
        </button>
      </div>

       {errorMessage && (
         <div className="model-assessment-state model-assessment-state-failed" role="alert">
           <strong>Model assessment did not complete.</strong>
           <p>{errorMessage}</p>
           <p className="muted-copy">Deterministic analysis remains available and authoritative.</p>
         </div>
       )}

      {!errorMessage && status === "idle" && (
        <p className="muted-copy">Run the separate model assessment endpoint to compare an advisory model view of the current email.</p>
      )}

      {!errorMessage && status === "not_configured" && (
           <div className="model-assessment-state model-assessment-state-not-configured">
           <strong>Model assessment is not configured yet.</strong>
           <p className="muted-copy">The endpoint is available, but no experimental local model is configured for this runtime.</p>
         </div>
       )}

       {!errorMessage && status === "failed" && assessment && (
         <div className="model-assessment-state model-assessment-state-failed" role="alert">
           <strong>Model assessment did not complete.</strong>
           <p>{assessment.error_message || "The model did not return an advisory result."}</p>
           <p className="muted-copy">Deterministic analysis remains available and authoritative.</p>
         </div>
       )}

       {!errorMessage && status === "completed" && assessment && (
         <div className="model-assessment-state model-assessment-state-completed" aria-live="polite">
           <div className="model-result-summary">
             <span className="model-result-label">Advisory model result</span>
             <div className="model-result-heading">
               <strong>{assessment.label}</strong>
               <span className="model-confidence">
                 Confidence: {assessment.confidence === null ? "Not available" : assessment.confidence.toFixed(2)}
               </span>
             </div>
             <p>{assessment.summary || "The model returned no summary."}</p>
           </div>

           <div className="model-assessment-detail-grid">
             <div>
               <span className="summary-label">Signals</span>
               <p>{assessment.signals.length === 0 ? "No model signals" : assessment.signals.join(", ")}</p>
             </div>
             <div>
               <span className="summary-label">Model traceability</span>
               <p>{assessment.model_name || "Model name unavailable"}</p>
               <p className="muted-copy">Version: {assessment.model_version || "Not available"}</p>
             </div>
           </div>
         </div>
       )}
    </section>
  );
}
