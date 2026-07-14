import type { ExtractedEvidenceResponse } from "../../types/api";

import { displayValue } from "./shared";


type ExtractedEvidenceProps = {
  extractedEvidence: ExtractedEvidenceResponse;
};


export function ExtractedEvidence({ extractedEvidence }: ExtractedEvidenceProps) {
  return (
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
  );
}
