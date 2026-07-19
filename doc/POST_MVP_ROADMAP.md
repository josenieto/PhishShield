# Post-MVP Roadmap

## Purpose

This document defines the recommended work groups after the validated MVP v0.1 release-candidate baseline.

Its role is to separate post-MVP priorities from the already closed MVP scope so future development stays intentional instead of accumulating unrelated improvements opportunistically.

---

## Current Baseline

The current validated baseline is:

- `v0.1.0-rc.1` for the MVP local email-triage flow.

The MVP baseline already includes:

- backend FastAPI upload analysis for `.eml` files;
- deterministic Domain/Application analysis for domain, URL, attachment, authentication, social-engineering, scoring, and findings;
- frontend analyst workbench layout with upload, result rendering, and Markdown export;
- realistic scoring calibration baseline backed by benign and suspicious `.eml` fixtures;
- Docker Compose runtime validation for health, benign analysis, suspicious analysis, and upload-limit behavior;
- CI coverage for backend tests, frontend tests/build, and backend Docker smoke.

Post-release-candidate hardening already completed after the tag includes:

- local `pre-commit` guardrails for hygiene, Domain/Application boundaries, commit-message format, and scoring-sensitive changes;
- HTML anchor `href` URL extraction in the Python email parser adapter.

---

## Guiding Rules

- Keep the current hexagonal architecture intact: `Domain <- Application <- Infrastructure / Entrypoints`.
- Keep `Domain` pure and deterministic.
- Keep extraction from `.eml`, HTML, files, network responses, or external tools inside Infrastructure adapters or behind Application ports.
- Do not change scoring weights or critical indicators without fixture evidence and calibration documentation.
- Keep native-first development as the default. Docker remains a runtime/packaging path, not a mandatory development prerequisite.
- Treat local `pre-commit` guardrails as development protection, while keeping CI as the shared enforcement layer when stricter stabilization becomes necessary.
- Do not open OCR, YARA, browser-evidence, PDF/Office parsing, or model-inference implementation until a dedicated roadmap group explicitly starts that work.

---

## Recommended v0.2 Tracks

### Track 1: Report And Export v2

This initial block is now complete.

Candidate steps:

- add copy-to-clipboard for the Markdown report; Done after the first post-MVP roadmap planning step.
- add report preview before download; Done after the third Report And Export v2 step.
- add JSON export for the raw structured analysis result; Done after the second Report And Export v2 step.
- add simple HTML export when the Markdown flow is stable; Done after the fourth Report And Export v2 step.
- add optional analyst notes or a case-summary section if a real workflow needs it.

Keep out of scope for this track:

- PDF export unless a concrete analyst workflow justifies it;
- backend-generated reporting infrastructure unless frontend-only export becomes insufficient.

### Track 2: Parser And Runtime Polish

The parser now extracts URLs from visible text and HTML anchor `href` values.

Candidate steps:

- improve malformed HTML handling when real samples expose gaps;
- handle additional HTML link variants if fixtures show missing extraction behavior;
- add unusual charset edge cases only when realistic emails expose them;
- review deeply nested multipart behavior if real samples justify it;
- improve parser/runtime diagnostics without moving business logic into adapters.

Keep out of scope for this track:

- browser rendering;
- JavaScript execution;
- short-link resolution;
- PDF or Office parsing.

### Track 3: Frontend Analyst Polish

The frontend workbench is already usable, but still has room for UI polish.

Candidate steps:

- improve result hierarchy and severity visual language inside the current workbench;
- improve evidence density and analyst scanning speed on desktop;
- refine mobile responsiveness without changing the core flow;
- add more focused `AnalysisResults` tests if the component hierarchy grows;
- revisit wording only when realistic fixtures reveal confusing presentation.

Keep out of scope for this track:

- routing;
- persisted history;
- frontend Docker image;
- screenshots or browser evidence rendering.

### Track 4: Scoring And Calibration Maintenance

The current scoring baseline is already broad enough for the MVP.

Candidate steps:

- add new fixtures only when tied to a concrete calibration question;
- keep subtle suspicious cases visible without making them automatically critical;
- review whether support-, billing-, or QR-themed wording needs narrower or broader terms only when fixtures justify it;
- keep `doc/SCORING_CALIBRATION.md` as the source of truth before changing weights.

### Track 5: Dev And CI Guardrail Maturation

Local `pre-commit` guardrails are now in place.

Candidate steps:

- observe local hook ergonomics over normal development;
- defer CI integration until the local hook set proves stable and useful;
- later introduce CI enforcement incrementally, starting with hygiene and architecture checks before any scoring-specific PR guard;
- avoid turning local hooks into a full replacement for tests or CI.

### Track 6: Future Inference And ML Architecture Planning

This track is planning-only at first.

Candidate steps:

- define an `Application` port for model-assisted assessment;
- define an `Infrastructure` adapter boundary for local model execution;
- separate deterministic evidence from model assessment in the UI and API contract;
- define what confidence, explanation, and analyst override should mean before implementation begins.

Keep out of scope for this track:

- real model integration;
- Ollama-specific implementation work;
- ONNX runtime integration;
- prompt chains or agent workflows.

---

## Explicitly Deferred

These areas remain deferred until a dedicated roadmap group starts them:

- OCR;
- YARA scanning;
- Playwright/browser evidence capture;
- PDF link extraction;
- Office document and macro parsing;
- short-link resolution;
- attachment hash intelligence lookups;
- frontend Docker packaging;
- persisted analysis history;
- production hosting/distribution strategy beyond the current local runtime baseline;
- real AI/model inference implementation.

---

## Recommended Next Group

The current recommended next group is:

```text
Frontend Analyst Polish
```

Rationale:

- the initial Report And Export v2 block already delivered Markdown copy, preview, download, JSON export, and HTML export;
- the frontend workbench is stable enough that the next user-facing value comes from improved hierarchy, scanability, and analyst ergonomics;
- parser/runtime polish remains important, but it is better driven by real samples than by opening another broad product-facing block immediately.
