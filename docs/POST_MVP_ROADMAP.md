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

The initial parser/runtime hardening round is complete.

Completed scope:

- visible HTML extraction and `href` handling;
- script/style exclusion;
- non-standard charset fallback;
- nested and malformed multipart handling;
- HTML fallback when plain text is empty;
- real attachment and inline resource classification;
- parser fixture and integration coverage for the current extracted representation.

Future parser work is maintenance-driven and requires a realistic sample to demonstrate
a concrete gap.

Keep out of scope for this track:

- browser rendering;
- JavaScript execution;
- short-link resolution;
- PDF or Office parsing.

### Track 2.5: CLI And CI/CD Automation

The single-email deterministic CLI contract is now implemented. Batch and
security-platform formats remain deferred until a concrete workflow justifies
them.

The initial CLI contract is also covered by CI smoke tests for JSON output and
threshold exit behavior. This closes the single-email CLI stabilization step.

A reusable GitHub Actions workflow now supports the concrete artifact workflow:
it downloads exactly one `.eml`, runs the deterministic CLI, uploads the JSON
report, and enforces the configured risk threshold. The advisory model remains
outside this workflow.

A manual same-repository smoke caller is included to validate that adoption
path without requiring a downstream repository or real email data.

The goal is to make the deterministic analysis flow usable from local scripts and
CI/CD pipelines without creating a second analysis engine.

Candidate steps:

- add a CLI entrypoint for one `.eml` file;
- support human-readable text and structured JSON output;
- define stable exit codes and a configurable `--fail-on` risk threshold;
- add batch and JSONL output when a real workflow needs it;
- add Markdown or SARIF output only when a concrete reporting or security-platform integration justifies it;
- document CI examples and artifact handling.

Implemented first CLI contract:

```text
phishshield analyze path/to/email.eml --format text|json --fail-on none|low|medium|high|critical
```

Exit codes are stable:

```text
0  analysis completed and threshold not reached
1  analysis completed and --fail-on threshold reached
2  usage or argument error
3  file missing or unreadable
4  email invalid or analysis failed
```

Keep out of scope for the first CLI step:

- duplicating parser, scoring, or finding logic outside Application use cases;
- making model assessment a default CI gate;
- representing deterministic triage as a malware verdict;
- implementing batch, SARIF, or model automation before the single-email CLI contract is stable.

### Track 3: Frontend Analyst Polish

This track is complete.

The first frontend analyst polish step already grouped report actions more clearly inside the analysis results view.

Completed scope:

- result hierarchy and severity visual language inside the current workbench;
- evidence density and analyst scanning speed for sender, subject, findings, URLs, attachments, and authentication;
- responsive behavior without changing the core flow;
- focused result and export-flow tests;
- explicit experimental/advisory presentation for model assessment states.

Keep out of scope for this track:

- routing;
- persisted history;
- frontend Docker image;
- screenshots or browser evidence rendering.

Future frontend changes should be driven by new backend evidence or concrete analyst
workflow feedback rather than another broad polish block.

### Track 4: Scoring And Calibration Maintenance

The current scoring baseline is already broad enough for the MVP.

Candidate steps:

- add new fixtures only when tied to a concrete calibration question;
- keep subtle suspicious cases visible without making them automatically critical;
- review whether support-, billing-, or QR-themed wording needs narrower or broader terms only when fixtures justify it;
- keep `docs/SCORING_CALIBRATION.md` as the source of truth before changing weights.

### Track 5: Dev And CI Guardrail Maturation

Local `pre-commit` guardrails are now in place.

CI Phase 1 is now also enabled for hygiene, private-key detection, and
Domain/Application architecture boundaries. The scoring-sensitive guard remains
local-only until the CI guardrail set proves stable.

Candidate steps:

- observe local hook ergonomics over normal development;
- defer CI integration until the local hook set proves stable and useful;
- keep Phase 1 CI checks limited to hygiene, secrets, and architecture;
- later introduce CI enforcement incrementally, starting with hygiene and architecture checks before any scoring-specific PR guard;
- avoid turning local hooks into a full replacement for tests or CI.

### Track 6: Future Inference And ML Architecture Planning

The architecture and experimental runtime integration are complete. The active work
is advisory inference validation and family-based coverage strategy.

The first step in this track is to define a separate model-assessment endpoint that analyzes the original raw email in parallel with the deterministic branch.

The intended direction for this track is project-owned local inference rather than a user-installed AI runtime.

Candidate steps:

- define an `Application` port for model-assisted assessment;
- define an `Infrastructure` adapter boundary for local model execution;
- define a separate `/analyze-email-model-assessment` strategy instead of changing the current deterministic endpoint;
- research public phishing email datasets and define the training/evaluation path before choosing a runtime format;
- separate deterministic evidence from model assessment in the UI and API contract;
- define what confidence, explanation, and analyst override should mean before implementation begins.

Keep out of scope for this track:

- real model integration;
- forcing users to install an external AI runtime;
- prompt chains or agent workflows.

The intended expansion path is:

```text
1. Define validated model scope.
2. Add independent evidence by email family.
3. Measure coverage, abstention, and confident errors.
4. Expand scope only after promotion criteria are met.
```

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
Evidence-Driven Deterministic Workflow Expansion
```

Rationale:

- the initial Report And Export v2 block is complete;
- the Frontend Analyst Polish block is complete;
- the initial parser/runtime hardening round is complete;
- the extracted representation can now be held stable for model evaluation;
- the deterministic CLI contract and CI smoke checks are complete;
- model-assisted inference is closed as experimental and remains optional;
- future work should be driven by an actual analyst or CI workflow rather than another generic model-validation campaign.
