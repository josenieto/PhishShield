import type { ExtractedEvidenceResponse } from "../../types/api";

import { displayValue } from "./shared";


type ExtractedEvidenceProps = {
  extractedEvidence: ExtractedEvidenceResponse;
};


function authenticationClassName(result: string): string {
  const normalizedResult = result.trim().toLowerCase();
  if (normalizedResult === "pass") {
    return "auth-item auth-item-pass";
  }

  if (normalizedResult === "") {
    return "auth-item auth-item-empty";
  }

  return "auth-item auth-item-review";
}


export function ExtractedEvidence({ extractedEvidence }: ExtractedEvidenceProps) {
  return (
    <section className="findings-panel">
      <div className="panel-heading">
        <h2>Extracted evidence</h2>
        <p>Normalized message details extracted by the backend before indicator analysis.</p>
      </div>

      <div className="evidence-grid">
        <article className="evidence-card evidence-card-emphasis evidence-card-identity" aria-label="Sender domain evidence">
          <span className="summary-label">Sender domain</span>
          <strong>{displayValue(extractedEvidence.sender_domain)}</strong>
        </article>

        <article className="evidence-card evidence-card-wide evidence-card-emphasis evidence-card-subject" aria-label="Subject evidence">
          <span className="summary-label">Subject</span>
          <strong>{displayValue(extractedEvidence.subject)}</strong>
        </article>

        <article className={`evidence-card evidence-card-wide evidence-card-links${extractedEvidence.urls.length > 0 ? " evidence-card-has-content" : ""}`} aria-label="URL evidence">
          <span className="summary-label">URLs</span>
          {extractedEvidence.urls.length === 0 ? (
            <p className="muted-copy">No URLs extracted</p>
          ) : (
            <>
              <span className="evidence-count">{extractedEvidence.urls.length} extracted</span>
            <ul className="evidence-list">
              {extractedEvidence.urls.map((url) => (
                <li key={url} className="evidence-list-item">
                  <code className="evidence-code">{url}</code>
                </li>
              ))}
            </ul>
            </>
          )}
        </article>

        <article className={`evidence-card evidence-card-attachments${extractedEvidence.attachment_filenames.length > 0 ? " evidence-card-has-content" : ""}`} aria-label="Attachment evidence">
          <span className="summary-label">Attachments</span>
          {extractedEvidence.attachment_filenames.length === 0 ? (
            <p className="muted-copy">No attachments extracted</p>
          ) : (
            <>
              <span className="evidence-count">{extractedEvidence.attachment_filenames.length} extracted</span>
            <ul className="evidence-list">
              {extractedEvidence.attachment_filenames.map((filename) => (
                <li key={filename} className="evidence-list-item">
                  <code className="evidence-code">{filename}</code>
                </li>
              ))}
            </ul>
            </>
          )}
        </article>

        <article className="evidence-card evidence-card-wide evidence-card-emphasis evidence-card-authentication" aria-label="Authentication evidence">
          <span className="summary-label">Authentication results</span>
          <dl className="auth-grid">
            <div className={authenticationClassName(extractedEvidence.authentication_results.spf_result)}>
              <dt>SPF</dt>
              <dd>{displayValue(extractedEvidence.authentication_results.spf_result)}</dd>
            </div>
            <div className={authenticationClassName(extractedEvidence.authentication_results.dkim_result)}>
              <dt>DKIM</dt>
              <dd>{displayValue(extractedEvidence.authentication_results.dkim_result)}</dd>
            </div>
            <div className={authenticationClassName(extractedEvidence.authentication_results.dmarc_result)}>
              <dt>DMARC</dt>
              <dd>{displayValue(extractedEvidence.authentication_results.dmarc_result)}</dd>
            </div>
          </dl>
        </article>
      </div>
    </section>
  );
}
