# Changelog

All notable changes to PhishShield are recorded here.

---

## Unreleased

Future changes will be recorded here after the `v0.1.0-rc.2` release candidate.

---

## v0.1.0-rc.2 - Release Candidate

### Added

- Versioned frontend and backend images published to GitHub Container Registry.
- Analyst-focused Web UI with real MVP screenshots and documentation navigation.
- Deterministic single-email CLI with text/JSON output and stable exit codes.
- Reusable GitHub Actions workflow for `.eml` artifact analysis.
- Complete local Docker Compose deployment with frontend Nginx proxy and internal backend.
- Phase-one CI guardrails for hygiene, private-key detection, and architecture boundaries.
- MIT license, contribution guidance, security policy, and public roadmap.
- Documentation index for users, operators, integrators, contributors, and researchers.

### Validated

- Backend test suite and frontend test/build workflow.
- Backend Docker smoke and complete Compose smoke through the frontend proxy.
- Benign and suspicious deterministic analysis through the Web UI and artifact workflow.
- Markdown, JSON, and HTML report exports.
- Optional advisory model remains disabled by default and separate from deterministic results.

### Experimental

- Scope-aware local advisory inference with structured abstention reasons.
- Advisory inference is disabled by default, not a CI gate, and not product-ready.

### Deferred

- Production-grade ML promotion and family-specific training with authorized data.
- Batch CLI, JSONL batch output, and SARIF integration.
- OCR, YARA, PDF/Office and macro analysis, browser evidence capture, and link resolution.
- Persistence, accounts, multi-user operation, and hosted cloud deployment.

### Added

- MIT license, contribution guidance, security policy, and public roadmap.
- Documentation index for users, operators, integrators, contributors, and researchers.
- Complete Docker Compose smoke validation through the production frontend proxy.
- Local `pre-commit` guardrails for hygiene, commit-message validation, Domain/Application boundary checks, and scoring-sensitive change protection.
- HTML anchor `href` extraction and additional HTML `href` variant coverage in the Python email parser adapter.
- Markdown report copy action, Markdown report preview, JSON export, and HTML export in the frontend analyst workbench.

### Changed

- Improved the analyst workbench presentation by grouping report actions and refining risk, evidence, and findings hierarchy.
- Aligned post-MVP roadmap and next-step documentation after closing the initial `Report And Export v2` block.

---

## v0.1.0-rc.1 - 2026-07-06

### Added

- FastAPI backend upload analysis flow for `.eml` messages.
- Deterministic Domain/Application analysis for domain, URL, attachment metadata, authentication, social engineering, scoring, and findings.
- React + TypeScript + Vite analyst workbench frontend for upload and result inspection.
- Extracted evidence rendering for sender, subject, URLs, attachment filenames, and authentication results.
- Grouped findings with backend-provided category, severity, and explanation text.
- Markdown report download for the current frontend analysis result.
- Docker Compose backend runtime with runtime configuration support.
- Backend CI, frontend test/build CI, and backend Docker smoke validation.
- Realistic scoring calibration baseline backed by benign and suspicious `.eml` fixtures.

### Validated

- Full backend test suite.
- Frontend test suite and production build.
- Docker runtime health, benign-analysis, suspicious-analysis, and upload-limit smoke checks on a Docker-enabled environment.

### Deferred

- OCR.
- YARA scanning.
- Playwright/browser evidence capture.
- PDF link extraction.
- Office document and macro parsing.
- Short-link resolution.
- Attachment hash intelligence lookups.
- Frontend Docker packaging.
- Persisted analysis history.
- Production hosting and distribution beyond the current local runtime baseline.
- Real AI or model-inference implementation.
