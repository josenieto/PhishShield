# Changelog

All notable changes to PhishShield are recorded here.

---

## Unreleased

### Added

- MIT license, contribution guidance, security policy, and public roadmap.
- Documentation index for users, operators, integrators, contributors, and researchers.
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
