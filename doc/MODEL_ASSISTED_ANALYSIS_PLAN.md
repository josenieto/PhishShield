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

### Experimental sklearn adapter plan

The first real model adapter should be explicitly experimental and disabled unless runtime configuration points to a local artifact.

Planned adapter name:

```text
SklearnModelAssessmentAdapter
```

Runtime configuration:

```text
PHISHSHIELD_MODEL_ASSESSMENT_ENABLED=true
PHISHSHIELD_MODEL_ARTIFACT_PATH=path/to/phishshield_baseline_candidate.joblib
PHISHSHIELD_MODEL_METADATA_PATH=path/to/phishshield_baseline_candidate.metadata.json
```

The current experimental artifact is stored outside Git:

```text
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\models\phishshield_baseline_candidate.joblib
C:\Users\nieto006\AppData\Local\Temp\opencode\phishshield-datasets\models\phishshield_baseline_candidate.metadata.json
```

Adapter behavior:

- return `not_configured` when model assessment is disabled or paths are missing;
- load the `joblib` pipeline and metadata only from configured local paths;
- parse the raw email with the existing email parser adapter;
- build the same `text_with_light_metadata` representation used during training;
- compute label and suspicious probability with the loaded model;
- map the result into `ModelAssessment` without changing deterministic findings or risk score;
- return `failed` with a safe error message if loading, parsing, feature conversion, or prediction fails.

Feature construction must match the selected baseline:

```text
subject + body_text + urls + attachment_filenames
```

Initial response mapping:

```text
status: completed
label: benign | suspicious
confidence: suspicious probability when label is suspicious, otherwise benign probability
summary: short advisory text derived from label and confidence
signals: model metadata and top-level feature-family notes, not deterministic finding codes
model_name: metadata.model_name
model_version: metadata.git_commit or metadata.created_at until explicit versions exist
```

The adapter must not:

- write artifacts;
- train models;
- fetch remote resources;
- open URLs;
- execute attachments;
- require any external AI runtime;
- make deterministic analysis depend on model success.

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

Experimental sklearn adapter failure mapping:

| Condition | Expected status | Notes |
|---|---|---|
| model assessment disabled | `not_configured` | Default behavior. |
| artifact path missing | `not_configured` | Do not treat as server failure. |
| metadata path missing | `not_configured` | Metadata is required for safe advisory output. |
| artifact load error | `failed` | Include safe error text, no stack trace. |
| metadata parse error | `failed` | Include safe error text, no raw metadata dump. |
| email parser failure | `failed` | Deterministic endpoint remains unaffected. |
| prediction failure | `failed` | Deterministic endpoint remains unaffected. |

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

For the experimental sklearn adapter planning step, these are also non-goals:

- enabling the model by default;
- committing model artifacts;
- defining a production model release process;
- combining model output into deterministic scoring;
- changing frontend risk semantics.

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

Implemented planning step:

```text
docs(ml): Define first training and evaluation strategy.
```

Scope:

- choose binary vs multi-class baseline target;
- define first feature set;
- define dataset split and holdout policy in more detail;
- define metrics and acceptance criteria for moving beyond the noop adapter;
- still no training implementation.

This phase is documented in:

- `doc/ML_TRAINING_EVALUATION_STRATEGY.md`

### Phase 8: Experimental Embedded Local Adapter

Implemented step:

```text
feat(ml): Add experimental sklearn model assessment adapter.
```

Completed scope:

- load the exported experimental `joblib` artifact and metadata from explicit configuration;
- keep the adapter disabled by default;
- convert raw emails into the selected `text_with_light_metadata` feature representation;
- return advisory `ModelAssessment` output;
- preserve `not_configured` behavior when config is absent;
- cover configured, not-configured, and failed-load cases with unit tests;
- avoid API/frontend behavior changes until the adapter is proven in isolation.

Implemented adapter:

```text
SklearnModelAssessmentAdapter
```

The adapter is intentionally isolated in Infrastructure. It is not wired into API configuration yet.

Observed behavior:

- missing artifact or metadata path returns `not_configured`;
- configured artifact and metadata return `completed` with label, confidence, model metadata, and advisory signals;
- artifact load errors and unsupported metadata feature sets return `failed`;
- deterministic analysis remains unaffected.

Out of scope for this phase:

- production artifact packaging;
- frontend copy or design changes;
- combined deterministic/model scoring;
- automatic model download.

### Phase 9: Runtime Configuration Wiring

Implemented step:

```text
feat(api): Wire experimental model assessment adapter through config.
```

Completed scope:

- add runtime settings for enabling model assessment;
- read artifact and metadata paths from configuration;
- keep `NoopModelAssessmentAdapter` as the default;
- use `SklearnModelAssessmentAdapter` only when explicitly enabled and paths are configured;
- add API tests for configured, not-configured, and failed adapter behavior.

Runtime settings:

```text
PHISHSHIELD_MODEL_ASSESSMENT_ENABLED=true
PHISHSHIELD_MODEL_ARTIFACT_PATH=path/to/phishshield_baseline_candidate.joblib
PHISHSHIELD_MODEL_METADATA_PATH=path/to/phishshield_baseline_candidate.metadata.json
```

Current behavior:

- model assessment remains disabled by default;
- missing or disabled config returns the existing `not_configured` response;
- configured local artifact paths enable the experimental sklearn adapter;
- the endpoint remains separate from `/analyze-email`;
- deterministic analysis is not affected by model configuration.

Out of scope:

- frontend changes beyond existing model panel behavior;
- production artifact release;
- deterministic/model score merging.

### Phase 10: Runtime Validation And UI Copy

Planned next implementation step:

```text
test(ml): Validate configured experimental model endpoint.
```

Planned scope:

- run the configured endpoint against the exported artifact outside Git;
- verify response shape and advisory copy from the existing frontend panel;
- document local configuration steps;
- keep the feature experimental and disabled by default.

---

## Open Questions

1. Which public datasets are reliable enough to support a first project-owned phishing-email model?
2. What maximum raw email size should the model branch accept independently of the deterministic upload limit?
3. Should attachments be ignored, summarized, or partially represented in the first model input format?
4. What confidence representation is understandable enough for analysts without overstating certainty?
5. At what point, if any, should model output influence a combined assessment rather than stay advisory?
