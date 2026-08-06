---
name: phishshield-backend
description: Specialized guidance for backend work in PhishShield. Use this skill whenever the user asks to create, modify, or review Python/FastAPI code, Application use cases, ports, adapters, Pydantic models, API endpoints, parsers, backend forensic modules, Playwright/Ollama/YARA/OCR integration, backend Docker setup, or Pytest tests around backend boundaries. Also use it when a task mentions Domain/Application/Infrastructure, contracts, DTOs, validation, or .eml analysis from the backend, even if the user does not explicitly say "backend". For pure Domain indicator helpers, prefer phishshield-testing and phishshield-security-analysis. If the task requires deciding layer boundaries or general architecture, apply phishshield-architecture first and then return to this skill for backend implementation.
---

# phishshield-backend

## Purpose

Help AI agents develop the **PhishShield** backend while respecting the project ADR and avoiding a flat FastAPI-coupled implementation.

PhishShield is a defensive local/self-hosted tool for forensic analysis of `.eml` email files. The backend concentrates analysis rules, use case orchestration, technical adapters, and API entrypoints. Therefore, separation between domain, application, and infrastructure is critical: it allows parsers, sandboxing, local AI, or frameworks to change without breaking the system core.

## References to consult

Before making relevant backend changes, read:

- `AGENT.md`
- `docs/ADR.md`
- `.skills/README.md`

If this skill conflicts with `docs/ADR.md`, the ADR takes precedence.

## Working process

When this skill triggers:

1. Identify whether the task is backend implementation or an architectural decision.
2. If there are doubts about layers, boundaries, or dependencies, apply `phishshield-architecture` first.
3. Locate the affected layer: `Domain`, `Application`, `Infrastructure`, or `Entrypoints`.
4. If the task is only a pure `Domain` indicator helper, prefer `phishshield-testing` and `phishshield-security-analysis` instead of expanding backend infrastructure.
5. Design contracts before adapters when IO, network, sandboxing, AI, OCR, YARA, or external parsers are involved.
6. Keep FastAPI as a thin entrypoint.
7. Add or update tests if behavior changes.
8. Close with a short check against the backend checklist.

The goal is to produce implementable backend code without degrading hexagonal architecture.

## When to use this skill

Use this skill for tasks related to:

- Python and FastAPI;
- endpoint design;
- application use cases;
- ports and adapters;
- domain models;
- DTOs and Pydantic validation;
- `.eml`, PDF, Office, image, or URL parsing;
- SPF/DKIM/DMARC modules;
- homoglyph, Punycode, or short URL analysis;
- backend integration with Playwright, Ollama, Tesseract, YARA, or oletools;
- backend error handling;
- unit or integration tests with Pytest;
- backend service Docker setup.

Do not use this skill for purely frontend tasks unless they involve API contracts or shared models.

Do not use this skill as the primary guide for isolated pure `Domain` helpers. For those tasks, use `phishshield-testing` for the TDD workflow and `phishshield-security-analysis` for forensic indicator boundaries.

## Expected response shape

When using this skill, structure the solution as follows when applicable:

```text
1. Affected layer
2. Proposed design
3. Required contracts or models
4. Involved adapters or endpoints
5. Error handling, limits, and security
6. Recommended Pytest tests
7. Architectural risks avoided
```

If the task requires a prior architectural decision, state that and route first to `phishshield-architecture`.

## Required mental model

Work with this dependency direction:

```text
Domain  <-  Application  <-  Infrastructure / Entrypoints
```

Interpret the layers as:

- **Domain**: pure models and forensic logic free from frameworks.
- **Application**: use cases and ports orchestrating the analysis.
- **Infrastructure**: concrete adapters, FastAPI, parsers, Playwright, Ollama, YARA, OCR, network, filesystem, and Docker.

The reason is to keep the analysis core stable even when libraries, frameworks, or external services change.

## Domain rules

In `Domain`:

- Define pure models such as `Email`, `AnalysisResult`, artifacts, indicators, attachments, or findings.
- Implement deterministic pure logic when possible, for example normalization, indicator classification, or homoglyph detection.
- Do not import FastAPI.
- Do not import external SDKs.
- Do not perform filesystem, network, database, or process IO.
- Do not call Playwright, Ollama, Tesseract, oletools, YARA, or infrastructure libraries directly.
- Do not depend on environment variables.

If a function needs network, browser, OCR, AI, or parsing through an external library, it probably belongs in an infrastructure adapter behind a port.

## Application rules

In `Application`:

- Define use cases representing system actions, for example analyzing an `.eml`, extracting artifacts, evaluating links, or generating a report.
- Define ports as abstract interfaces for external capabilities.
- Coordinate modules, but do not implement concrete technical details.
- Depend on the domain and abstractions, not adapters.
- Keep orchestration policies visible and testable.

Reasonable port examples:

```python
class LinkAnalyzerPort(Protocol):
    def analyze(self, links: list[str]) -> list[LinkFinding]:
        ...
```

```python
class SandboxBrowserPort(Protocol):
    async def capture(self, url: str) -> SandboxResult:
        ...
```

```python
class AiAnalysisPort(Protocol):
    async def explain(self, analysis: AnalysisResult) -> AiExplanation:
        ...
```

## Infrastructure rules

In `Infrastructure`:

- Implement concrete adapters for ports.
- Encapsulate FastAPI, Playwright, Ollama, OCR, YARA, oletools, pdfminer, PyPDF2, idna, HTTP requests, and filesystem.
- Translate technical errors into controlled application errors.
- Apply timeouts and resource limits.
- Treat all input as hostile: `.eml`, attachments, URLs, PDFs, Office documents, and images.
- Avoid implicit side effects.

Adapter examples:

- `FastApiEntrypoint`
- `OllamaAiAnalysisAdapter`
- `PlaywrightSandboxAdapter`
- `PdfAttachmentParserAdapter`
- `OfficeMacroScannerAdapter`
- `YaraScannerAdapter`
- `TesseractOcrAdapter`
- `HttpRedirectResolverAdapter`

## FastAPI rules

FastAPI must act as an entrypoint, not as the business core.

In endpoints:

- validate input;
- convert requests into application commands or DTOs;
- call use cases;
- convert results into responses;
- handle HTTP errors;
- do not implement forensic analysis directly in the endpoint;
- do not mix domain logic with FastAPI dependencies.

Recommended pattern:

```text
router -> request schema -> use case -> domain/application result -> response schema
```

## Pydantic rules

Use Pydantic for boundary input/output contracts and validation.

Distinguish:

- domain models: express business concepts;
- DTOs or Pydantic schemas: express external contracts;
- application commands: express use case intent.

Avoid using API Pydantic models as domain entities by default if that couples logic to the framework.

## Backend forensic module rules

PhishShield analyzes potentially malicious artifacts. Work defensively.

### `.eml` emails

- Parse robustly.
- Do not trust declared headers.
- Extract sender, subject, body, attachments, and links without executing content.
- Keep extraction from `.eml` in infrastructure adapters. Domain services should receive already extracted values and analyze them; do not place email-body URL extraction, attachment extraction, or header parsing helpers in Domain just because they can be implemented as pure functions.

### Headers

- Keep SPF, DKIM, and DMARC as verifiable results.
- Separate header parsing from risk interpretation.

### Links

- Normalize domains.
- Detect IDN/homoglyphs.
- Convert to Punycode when applicable.
- Resolve shorteners with passive requests and timeouts.
- Avoid following redirects without limits.

### Sandbox

- Use Playwright only from infrastructure.
- Run the browser isolated.
- Block downloads and persistence.
- Apply timeouts.
- Capture screenshot and title without exposing the host.

### Attachments

- Treat PDFs, Office files, and images as hostile input.
- Calculate SHA-256 when applicable.
- Extract PDF links without executing content.
- Detect macros with specialized tooling.
- Run YARA in a controlled way.

### Local AI

- AI is optional through configuration.
- Ollama belongs to infrastructure.
- AI complements deterministic results; it must not be the only source of truth.
- If `USE_AI_ANALYSIS=false`, the use case must continue cleanly without AI.

## Expected testing

When backend behavior changes, add or update tests.

Use Pytest with this strategy:

- Unit tests for domain and pure algorithms.
- Application tests using mocked ports.
- Adapter tests with controlled fixtures.
- Integration tests only when necessary.
- Do not depend on real network in unit tests.
- Do not depend on real external services to validate business rules.
- Use synthetic `.eml`, URL, header, and attachment fixtures.

Cases that deserve tests:

- homoglyphs and Punycode;
- parsed SPF/DKIM/DMARC results;
- link extraction;
- PDFs with embedded links;
- simulated Office macros;
- adapter failures;
- disabled AI;
- sandbox or network timeouts.

## Rejection criteria

Reject or redesign a backend solution if it:

- implements forensic analysis directly in a FastAPI endpoint;
- imports FastAPI, Playwright, Ollama, OCR, YARA, HTTP, or filesystem from `Domain`;
- instantiates concrete adapters inside use cases without injection;
- adds real network access to unit tests;
- uses local AI as the only source of truth for analysis;
- mixes API DTOs with domain entities without justification;
- ignores timeouts, limits, or hostile input in adapters.

## Checklist before finishing a backend task

- [ ] I read `docs/ADR.md` if the task affects architecture or main modules.
- [ ] Domain does not import infrastructure.
- [ ] Use cases depend on ports, not concrete adapters.
- [ ] FastAPI acts only as an entrypoint.
- [ ] External integrations are encapsulated in Infrastructure.
- [ ] Hostile input is validated and limited.
- [ ] Errors and timeouts are handled where appropriate.
- [ ] Tests were added or updated if behavior changed.
- [ ] The solution preserves the ADR local/self-hosted privacy approach.

## Examples

### Endpoint for `.eml` upload

Correct:

```text
FastAPI router receives file -> builds command -> calls AnalyzeEmailUseCase -> returns response.
```

Incorrect:

```text
FastAPI router parses headers, resolves links, calls Playwright, and calculates risk directly.
```

### New link analyzer

Correct:

```text
Application defines LinkAnalyzerPort.
Infrastructure implements IdnaLinkAnalyzerAdapter or HttpRedirectResolverAdapter.
Domain contains pure types and rules.
```

Incorrect:

```text
Domain imports requests/httpx to resolve redirects.
```

### Ollama integration

Correct:

```text
Application defines AiAnalysisPort.
Infrastructure implements OllamaAiAnalysisAdapter.
The use case skips AI cleanly when disabled.
```

Incorrect:

```text
The domain calls the ollama library directly.
```

## Suggested eval prompts

Use these prompts to test whether the skill guides the agent well:

1. `Create a FastAPI endpoint to upload an .eml file and start the full forensic analysis.`
2. `Implement a port and adapter to resolve shortened URLs without breaking hexagonal architecture.`
3. `Add Pytest tests for homoglyph domain detection and Punycode conversion.`
4. `Integrate Ollama as optional AI analysis controlled by USE_AI_ANALYSIS.`

A good answer should preserve layer separation, propose ports/adapters, and add tests when behavior changes.
