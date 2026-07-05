# Backend Evolution Plan

## Purpose

This document tracks PhishShield backend evolution after the first pure Domain iteration.

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
- attachment filenames;
- already computed SPF/DKIM/DMARC result tokens from `Authentication-Results` headers.

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
| Email Parser Robustness | In progress |
| Integration Tests | In progress |

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

Candidate steps:

- encoded sender and attachment filenames;
- multipart edge cases;
- HTML fallback edge cases;
- URL extraction edge cases;
- multiple `Authentication-Results` headers;
- Received-SPF fallback parsing if useful.

### 5. Integration Tests

Keep adding integration-style tests for important flows:

- text/plain raw email;
- HTML-only raw email;
- emails with attachments;
- emails with authentication headers;
- malformed but safely handled emails.

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
- Docker Compose runtime wiring.

---

## Decision Rule

Before adding a backend capability, decide whether it is:

- analysis of already extracted values: Domain/Application;
- orchestration of a system action: Application;
- extraction from external formats or IO: Infrastructure behind an Application port;
- external user/system exposure: Infrastructure entrypoint.

When in doubt, prefer a small contract or adapter step over mixing responsibilities across layers.
