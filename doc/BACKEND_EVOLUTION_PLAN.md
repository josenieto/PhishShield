# Backend Evolution Plan

## Purpose

This document tracks PhishShield backend evolution from the first pure Domain iteration through the current API, runtime, Docker, and CI MVP.

Its goal is to keep near-term backend work useful and maintainable while preserving the hexagonal architecture defined in `doc/ADR.md`.

---

## Current Baseline

The first pure Domain iteration is complete for the initial analysis groups:

- text normalization;
- homoglyph and suspicious Unicode analysis;
- domain analysis;
- URL analysis;
- attachment metadata analysis;
- authentication result analysis;
- social engineering heuristics;
- risk scoring;
- finding analysis;
- hash string validation.

Application now provides use cases for module-level analysis, finding summaries, risk scoring, extracted email analysis, and raw email analysis through a port.

Infrastructure currently includes a Python standard library email parser adapter that converts raw `.eml` bytes into `ExtractedEmailContent`.

---

## Architectural Principles

The backend must keep these boundaries explicit:

```text
Domain <- Application <- Infrastructure / Entrypoints
```

- Domain analyzes already extracted and normalized values.
- Application orchestrates use cases and defines ports.
- Infrastructure extracts data from external formats and implements ports.
- Entrypoints stay thin and translate external requests into application commands.

Extraction from external formats belongs in Infrastructure adapters or behind Application ports. Domain services must not extract data from `.eml`, HTML, PDFs, Office files, OCR output, byte streams, filesystem paths, network responses, or external tool output.

---

## Current Flow

```text
raw email bytes
    -> EmailContentExtractorPort
    -> PythonEmailContentExtractorAdapter
    -> ExtractedEmailContent
    -> AnalyzeRawEmailUseCase
    -> AnalyzeExtractedEmailUseCase
    -> technical analysis
    -> text analysis
    -> finding summary
    -> risk score
```

The flow is usable in tests and does not require filesystem access, FastAPI, external services, DNS, AI, OCR, YARA, Playwright, or PDF/Office parsers.

The current API surface is:

- `GET /health`
- `POST /analyze-email`

---

## Current Email Parser Scope

The current `PythonEmailContentExtractorAdapter` extracts:

- sender domain;
- decoded subject;
- plain text body;
- basic HTML-only body fallback;
- HTTP and HTTPS URLs from extracted body text;
- decoded attachment filenames;
- already computed SPF/DKIM/DMARC result tokens from `Authentication-Results` headers;
- SPF fallback result tokens from `Received-SPF` headers;
- repeated `Authentication-Results` and `Received-SPF` headers.

It intentionally does not perform:

- DNS SPF checks;
- DKIM cryptographic validation;
- DMARC policy lookup;
- short URL resolution;
- hash calculation;
- PDF or Office parsing;
- YARA scanning;
- OCR;
- AI analysis;
- browser sandboxing.

---

## Near-Term Roadmap

| Step | Status |
|---|---:|
| API Entrypoint | Done |
| API App Factory | Done |
| Input Limits And Error Handling | Done |
| Email Parser Robustness | Done |
| Fixture-Based Parser Integration Tests | Done |
| API Fixture Integration Tests | Done |
| Warning-Free Test Suite | Done |
| Runtime Config Readiness | Done |
| Docker Backend Runtime | Done |
| Backend CI And Docker Smoke | Done |
| API Documentation | Done |

### 1. API Entrypoint

Add the first FastAPI endpoint for raw email upload analysis.

Expected flow:

```text
FastAPI UploadFile
    -> bytes
    -> AnalyzeRawEmailCommand
    -> AnalyzeRawEmailUseCase
    -> AnalyzeEmailResponse
```

Constraints:

- keep the endpoint thin;
- do not implement forensic logic in the router;
- use existing response schemas;
- keep defaults private until configuration is introduced;
- avoid filesystem access in the first endpoint.

Status:

```text
Done
```

### 2. API App Factory

After the router exists, add a minimal FastAPI app factory and include the router.

Constraints:

- no global side-effect-heavy app setup;
- no database or external services;
- keep dependency wiring explicit and small.

Status:

```text
Done
```

### 3. Input Limits And Error Handling

Add upload size limits and controlled error responses before treating the API as public-facing.

Initial concerns:

- empty upload behavior;
- oversized upload behavior;
- malformed email behavior;
- parser failures;
- response stability.

Status:

```text
Done
```

### 4. Email Parser Robustness

Improve extraction incrementally with tests.

Covered steps:

- decoded subject headers;
- decoded attachment filenames;
- HTML-only fallback extraction;
- non-UTF-8 plain text body decoding;
- non-UTF-8 encoded subject decoding;
- URL extraction from extracted body text;
- multiple attachment extraction;
- multiple `Authentication-Results` headers;
- `Received-SPF` fallback parsing;
- `Received-SPF` result variants;
- multiple `Received-SPF` headers.

Remaining candidate steps:

- encoded sender display names if they become relevant for future adapters;
- additional unusual charset edge cases if real samples expose gaps;
- deeply nested multipart structures;
- parser failure behavior for malformed but safely handled emails.

### 5. Integration Tests

Keep adding integration-style tests for important flows:

Done:

- text/plain raw email analysis;
- HTML-only raw email analysis;
- authentication fixture parsing;
- `Received-SPF` fixture parsing;
- multipart attachment fixture parsing;
- multi-attachment fixture parsing;
- encoded subject and encoded attachment filename fixture parsing;
- unusual charset fixture parsing;
- malformed multipart fixture parsing;
- HTML-only fixture parsing;
- suspicious API upload fixture;
- benign API upload fixture;
- suspicious attachment API upload fixture.

Pending:

- API error-contract fixtures for malformed or unexpected uploads.

Malformed but parseable uploads now degrade to a controlled low-information analysis response. Unexpected analyzer failures remain mapped to `422` at the API boundary.

### 6. Current Quality Baseline

The current suite is warning-free and covers the raw email analysis flow through:

- parser unit tests;
- parser fixture integration tests;
- raw email use case integration tests;
- API upload fixture integration tests.

The backend also runs:

- locally with `uvicorn`;
- in Docker through the root `Dockerfile`;
- in Docker Compose through `compose.yaml`;
- in GitHub Actions through backend tests and a Docker health smoke workflow.

Coverage is currently available in observability mode only:

- backend: `python -m pytest --cov=src --cov-report=term-missing`
- frontend: `cd frontend && npm run test:coverage`

The project does not enforce coverage thresholds in CI yet. The current goal is to make coverage visible before deciding whether any gates are useful.

---

## Next Focus

The next recommended group is frontend MVP planning.

Short-term goals:

- keep `README.md` as a backend quickstart;
- keep `doc/API.md` as the external API contract reference;
- use the current backend API, Docker runtime, and CI baseline as the contract for a first frontend upload/results flow;
- use `doc/FRONTEND_MVP_PLAN.md` as the roadmap for current frontend work.

---

## Explicitly Deferred

These capabilities remain deferred until a dedicated port/adapter step is justified:

- DNS SPF validation;
- DKIM cryptographic validation;
- DMARC policy lookup;
- short URL resolution;
- screenshot sandboxing;
- PDF link extraction;
- Office macro analysis;
- attachment hash calculation from bytes or files;
- YARA scanning;
- OCR;
- Ollama or other AI integrations;
- frontend dashboard;
- multi-service Docker Compose runtime wiring.

---

## Decision Rule

Before adding a backend capability, decide whether it is:

- analysis of already extracted values: Domain/Application;
- orchestration of a system action: Application;
- extraction from external formats or IO: Infrastructure behind an Application port;
- external user/system exposure: Infrastructure entrypoint.

When in doubt, prefer a small contract or adapter step over mixing responsibilities across layers.
