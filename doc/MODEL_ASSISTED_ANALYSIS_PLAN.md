# Model-Assisted Analysis Plan

## Purpose

This document defines the planned architecture for future model-assisted email analysis in PhishShield.

Its goal is to describe how a project-owned local model can assess the original email in parallel with the deterministic engine without weakening the current explainable analysis flow.

This is still mostly a planning document. It now also records the application-level contract introduced before any real model runtime or endpoint exists.

---

## Decision Summary

PhishShield will keep the current deterministic analysis flow as the primary and authoritative analysis path.

Future model-assisted analysis should:

- analyze the original raw `.eml` email in parallel with the deterministic branch;
- be exposed through a separate API endpoint;
- remain optional and advisory;
- use a model artifact selected, trained, and packaged by the project rather than requiring a user-installed AI runtime;
- never replace deterministic findings, extracted evidence, or deterministic risk scoring in its first version.

---

## Project-Owned Inference Direction

PhishShield should own the future inference path end to end:

- dataset selection and evaluation;
- training or fine-tuning decisions;
- model artifact packaging;
- backend inference integration;
- release and versioning of the model artifact.

The project should not assume that users will install or operate a separate runtime such as Ollama for the first useful model-assisted analysis flow.

The preferred direction is:

```text
project-owned model artifact
    -> embedded local inference inside PhishShield
    -> no external AI runtime required for users
```

---

## Deterministic-First Principle

The current deterministic engine remains authoritative for:

- extracted evidence;
- finding codes;
- finding explanations;
- finding summaries;
- risk scoring.

The future model branch remains advisory until there is strong evidence that a later combined assessment should exist.

In practical terms:

```text
deterministic analysis = authoritative
model-assisted analysis = advisory
```

The UI and API must preserve that distinction clearly.

---

## Parallel Raw Email Model Branch

The intended future flow is:

```text
raw .eml bytes
    ├── deterministic branch
    │       -> EmailContentExtractorPort
    │       -> PythonEmailContentExtractorAdapter
    │       -> ExtractedEmailContent
    │       -> AnalyzeRawEmailUseCase
    │       -> findings, evidence, risk_score
    │
    └── model branch
            -> ModelAssessmentPort
            -> Infrastructure model adapter
            -> model_assessment
```

The deterministic branch and the model branch should consume the same uploaded email independently.

The model branch should not require the deterministic branch to succeed first, although the application layer may choose to orchestrate both under a higher-level use case later.

---

## Endpoint Strategy

The current deterministic endpoint remains unchanged:

```text
POST /analyze-email
```

Future model-assisted analysis should be exposed through a separate endpoint:

```text
POST /analyze-email-model-assessment
```

Why a separate endpoint:

- it keeps the current deterministic contract stable;
- it lets analysts request the model view only when needed;
- it keeps failure, latency, and configuration concerns away from the existing endpoint;
- it makes it easy to compare deterministic and model-assisted views of the same email.

This endpoint should accept the same multipart upload style as the current endpoint:

- field name: `file`
- content type: `message/rfc822`

---

## Application Boundary

The model branch is introduced through an `Application` port.

Introduced port name:

```text
ModelAssessmentPort
```

The port accepts a command-like input that represents the original uploaded email:

```text
raw_email: bytes
filename: str
content_type: str
max_input_bytes: int
```

The `Application` layer also defines:

```text
ModelAssessment
```

The current contract fields are:

```text
status
label
confidence
summary
signals
model_name
model_version
error_message
```

The `Application` layer must not depend on a concrete model backend.

---

## Future Infrastructure Boundary

Concrete implementations belong in `Infrastructure` adapters.

Possible future adapters include:

- `NoopModelAssessmentAdapter`
- `EmbeddedClassifierModelAssessmentAdapter`
- `EmbeddedOnnxModelAssessmentAdapter`

This planning step intentionally stays model-backend-agnostic. No concrete runtime format is selected yet.

The adapter is responsible for:

- safe preprocessing of raw email input for the selected model runtime;
- truncation and size limits;
- conversion of raw email bytes into the model-specific request shape;
- timeouts and failure handling;
- mapping model output into the application-level `ModelAssessment` contract.

---

## Response Contract Draft

The future endpoint should return a contract separate from deterministic findings.

Conceptual response:

```json
{
  "model_assessment": {
    "status": "completed",
    "label": "suspicious",
    "confidence": 0.84,
    "summary": "The message resembles an account verification phishing lure.",
    "signals": [
      "Credential verification wording",
      "Unusual link presentation"
    ],
    "model_name": "local-model-name",
    "model_version": "0.1",
    "error_message": ""
  }
}
```

Important response rules:

- `model_assessment` must not be mixed into `finding_codes`;
- `model_assessment` must not overwrite `risk_score`;
- the model branch may fail independently of the deterministic branch.

Expected statuses:

- `completed`
- `not_configured`
- `failed`
- `skipped`

---

## Frontend Presentation

The frontend should present the model branch separately from deterministic analysis.

Recommended UI split:

```text
Deterministic analysis
Model-assisted assessment
```

The frontend should make the distinction explicit with copy such as:

```text
Model-assisted assessment is advisory and does not replace deterministic findings.
```

The model output should not be rendered as if it were a deterministic finding or a backend-provided risk indicator.

---

## Privacy And Security Constraints

The future model branch must respect these constraints:

- local/self-hosted by default;
- no third-party cloud analysis by default;
- no external user-installed AI runtime required for the initial useful model-assisted flow;
- raw email content treated as untrusted input;
- explicit size limits for model input;
- no execution of links, attachments, scripts, or embedded content;
- prompt-injection-aware handling if an LLM backend is used;
- deterministic analysis must continue to function when the model branch is disabled or fails.

---

## Failure Modes

The architecture should handle these cases explicitly:

- model backend not configured;
- model timeout;
- model runtime error;
- input too large for the configured model limit;
- adapter preprocessing failure.

Failure in the model branch must not break deterministic analysis.

---

## Non-Goals

This planning block does not implement:

- a real model runtime;
- a real endpoint;
- a real application port;
- combined deterministic + model scoring;
- frontend UI for model output;
- model training pipeline;
- packaged model artifacts;
- prompt engineering;
- cloud-hosted inference.

---

## Phased Implementation Plan

### Phase 1: Architecture Planning

Completed.

Scope:

- raw-email parallel model branch;
- deterministic-first principle;
- separate endpoint strategy;
- project-owned local inference direction;
- supporting roadmap and ADR updates.

### Phase 1.5: Dataset And Training Research

Completed.

```text
docs(ml): Research public phishing email datasets.
docs(ml): Define dataset preparation pipeline.
```

Completed scope:

- identify public benign, phishing, and related fraud email corpora;
- review dataset license, quality, and age;
- define preparation rules for canonical samples, labels, normalization, deduplication, leakage prevention, and evaluation splits;
- avoid committing to a runtime backend before the dataset strategy is understood.

This phase is now documented in:

- `doc/ML_DATASET_RESEARCH.md`
- `doc/ML_DATA_PREPARATION_PLAN.md`

### Phase 2: Application Contract

Implemented step:

```text
feat(application): Add model assessment port contract.
```

Completed scope:

- `ModelAssessmentPort`;
- `AssessRawEmailWithModelCommand`;
- `ModelAssessment` result model;
- unit tests for the contract shape.

### Phase 3: Application Use Case

Implemented step:

```text
feat(application): Add raw email model assessment use case.
```

Completed scope:

- application use case that delegates raw email assessment through `ModelAssessmentPort`;
- no real model runtime.

### Phase 4: Noop Adapter

Implemented step:

```text
feat(infrastructure): Add noop model assessment adapter.
```

Completed scope:

- no-op or `not_configured` behavior;
- no real model runtime.

### Phase 5: Endpoint Skeleton

Implemented step:

```text
feat(api): Add model assessment endpoint skeleton.
```

Completed scope:

- `POST /analyze-email-model-assessment`;
- use the application use case and noop adapter;
- return a stable `not_configured` response;
- keep real model runtime deferred.

### Phase 6: Frontend Presentation Skeleton

Implemented step:

```text
feat(frontend): Add model-assisted assessment skeleton.
```

Completed scope:

- frontend client for the separate model-assessment endpoint;
- advisory model-assessment panel;
- loading, failure, and `not_configured` states;
- no real model runtime.

### Phase 7: Training And Evaluation Strategy

Recommended next step:

```text
docs(ml): Define first training and evaluation strategy.
```

Scope:

- choose binary vs multi-class baseline target;
- define first feature set;
- define dataset split and holdout policy in more detail;
- define metrics and acceptance criteria for moving beyond the noop adapter;
- still no training implementation.

### Phase 8: Experimental Embedded Local Adapter

Potential future step:

```text
feat(infrastructure): Add local model assessment adapter.
```

Scope depends on the selected model artifact format and should be decided only after the training and evaluation strategy is validated.

---

## Open Questions

1. Which public datasets are reliable enough to support a first project-owned phishing-email model?
2. What maximum raw email size should the model branch accept independently of the deterministic upload limit?
3. Should attachments be ignored, summarized, or partially represented in the first model input format?
4. What confidence representation is understandable enough for analysts without overstating certainty?
5. At what point, if any, should model output influence a combined assessment rather than stay advisory?
