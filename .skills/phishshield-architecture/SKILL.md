---
name: phishshield-architecture
description: Specialized guidance for architectural decisions in PhishShield. Use this skill whenever the user asks to define, modify, or review repository structure, hexagonal architecture, Clean Architecture, Domain/Application/Infrastructure layers, ports, adapters, entrypoints, module boundaries, dependencies, external technology integration, Docker Compose from an architectural perspective, ADRs, domain group checkpoints, or any decision that may affect maintainability. Also use it after completing a pure Domain function group and before moving upward to Application, Infrastructure, or entrypoints. Use it for backend, frontend, security, AI, or DevOps tasks when the main question is where code belongs, how to avoid coupling, whether a port/adapter is required, or whether a proposal contradicts doc/ADR.md.
---

# phishshield-architecture

## Purpose

Help AI agents make coherent architectural decisions for **PhishShield**, respecting the main ADR and preventing design drift that couples the domain to frameworks, libraries, or external services.

PhishShield is a defensive, local, self-hosted tool for forensic analysis of `.eml` email files. Its architecture must allow parsers, sandboxing, local AI, frontend, API, and analysis tools to be replaced without changing the core system.

This skill operates above a concrete backend, frontend, or DevOps task. Its role is to decide **boundaries, layers, responsibilities, and dependency direction**.

## References to consult

Before making or reviewing architectural decisions, read:

- `AGENT.md`
- `doc/ADR.md`
- `.skills/README.md`

If this skill conflicts with `doc/ADR.md`, the ADR takes precedence.

## Working process

When this skill triggers:

1. Identify the real architectural decision behind the request.
2. Consult `doc/ADR.md` if the task affects layers, modules, deployment, or integrations.
3. Classify the affected elements as `Domain`, `Application`, `Infrastructure`, or `Entrypoints`.
4. Detect dangerous dependencies or coupling to frameworks/libraries.
5. Propose the correct boundary using ports and adapters when IO, external tools, or future replacement are involved.
6. If a pure `Domain` group has just been completed, run a checkpoint before recommending any upward layer movement.
7. State which technical skill should continue the work if the architecture is already decided.
8. Close with a short check against the architecture checklist.

The goal is not to produce more documentation. The goal is to prevent decisions that make the system rigid.

## When to use this skill

Use this skill when the task involves:

- defining the initial repository structure;
- creating or reorganizing folders;
- deciding whether code belongs in `Domain`, `Application`, `Infrastructure`, or `Entrypoints`;
- creating ports;
- creating adapters;
- reviewing dependencies between layers;
- adding a new forensic module;
- completing a pure `Domain` function group and deciding whether to move to `Application`;
- integrating FastAPI, Playwright, Ollama, YARA, Tesseract, oletools, pdfminer, PyPDF2, idna, or other libraries;
- reviewing technical proposals;
- creating or updating ADRs;
- designing Docker Compose from the system architecture perspective;
- separating backend, frontend, and auxiliary services;
- evaluating whether an implementation breaks hexagonal architecture.

Do not use this skill for purely internal implementation details when the architecture is already decided. In that case, use the relevant technical skill, for example `phishshield-backend`.

## Expected response shape

When using this skill, structure the answer briefly and decisively:

```text
1. Architectural decision
2. Affected layer or layers
3. Recommended design
4. Required ports/adapters
5. Coupling risks avoided
6. Recommended tests or validations
7. Next technical skill to use, if applicable
```

If the user's proposal breaks the ADR, say so explicitly and provide a compatible alternative.

## Baseline architecture model

The ADR defines a **hexagonal modular monolith** combined with Clean Architecture.

Dependency model:

```text
Domain  <-  Application  <-  Infrastructure / Entrypoints
```

Interpretation:

- **Domain** contains pure forensic business concepts and rules.
- **Application** contains use cases and ports.
- **Infrastructure** contains technical adapters and integrations.
- **Entrypoints** expose the system to the outside world, for example through FastAPI.

The arrow indicates the allowed dependency direction. Outer layers may depend on inner layers. Inner layers must not depend on outer layers.

## Architecture rules

### 1. Keep the domain pure

The domain must not import:

- FastAPI;
- Playwright;
- Ollama;
- Docker;
- httpx/requests;
- Tesseract/pytesseract;
- oletools;
- yara-python;
- pdfminer/PyPDF2;
- persistence frameworks;
- environment variables;
- external SDKs.

The domain may contain:

- entities;
- value objects;
- pure rules;
- deterministic algorithms;
- finding classification;
- normalization without IO;
- result types.

Correct example:

```text
Domain contains the pure homoglyph detection rule.
Infrastructure uses idna or external libraries if technical adaptation is required.
```

### 2. Application orchestrates through ports

Application should contain:

- use cases;
- contracts;
- ports;
- analysis orchestration;
- application policies;
- application errors.

Application must not know concrete implementations.

Example:

```text
AnalyzeEmailUseCase depends on LinkAnalyzerPort, AttachmentScannerPort, and SandboxBrowserPort.
```

It must not depend on:

```text
PlaywrightSandboxAdapter
OllamaAiAdapter
PdfMinerParser
FastAPI UploadFile
```

### 3. Infrastructure implements technical details

Infrastructure contains concrete adapters:

- FastAPI API;
- `.eml` parser;
- PDF parser;
- Office scanner;
- YARA scanner;
- OCR;
- Playwright;
- Ollama;
- HTTP resolution;
- filesystem;
- Docker/runtime configuration.

Infrastructure translates between the external world and Application contracts.

### 3.1 Extraction belongs to adapters, analysis belongs to Domain

Infrastructure adapters must not use Domain services to extract data from external formats.

Domain services analyze already extracted and normalized values. They must not be responsible for extracting URLs, attachments, hashes, authentication results, text, metadata, or indicators from `.eml`, HTML, PDFs, Office files, OCR output, filesystem paths, byte streams, network responses, or external tool output.

Correct flow:

```text
raw .eml bytes
    -> Application port
    -> Infrastructure email parser adapter
    -> ExtractedEmailContent(urls=..., attachment_filenames=...)
    -> Application use case
    -> Domain URL / attachment / authentication analysis
```

Incorrect flow:

```text
Infrastructure email parser adapter
    -> Domain service for extracting URLs from email body
```

Examples:

- Extract URLs from email body: Infrastructure adapter or dedicated extraction port.
- Analyze an already extracted URL: Domain/Application.
- Extract attachment filenames from `.eml`: Infrastructure adapter.
- Analyze an already extracted attachment filename: Domain/Application.
- Extract SPF/DKIM/DMARC result strings from headers: Infrastructure adapter.
- Interpret SPF/DKIM/DMARC result strings: Domain/Application.
- Calculate a hash from bytes or files: Infrastructure adapter behind a port.
- Validate an already calculated hash string: Domain.

### 4. Entrypoints do not contain business rules

An entrypoint should:

- validate input;
- build commands or DTOs;
- call a use case;
- convert results to responses;
- map errors.

It must not implement forensic rules directly.

## Criteria for placing code

When placement is unclear, ask:

1. Does it represent a stable business rule or analysis concept?
   - Yes: `Domain`.

2. Does it orchestrate a system action through abstractions?
   - Yes: `Application`.

3. Does it depend on a library, protocol, framework, network, filesystem, or external process?
   - Yes: `Infrastructure`.

4. Does it expose an API or interface to an external user/system?
   - Yes: `Entrypoints` inside Infrastructure.

5. Should the library/tool be replaceable without changing the core?
   - If yes, create a port and an adapter.

## Port design

Create a port when a capability:

- requires IO;
- depends on an external library;
- may be replaced;
- must be mocked in tests;
- represents a boundary with infrastructure;
- is optional through configuration.

Good port candidates:

- link analysis;
- browser sandboxing;
- AI analysis;
- OCR extraction;
- YARA scanning;
- attachment parsing;
- redirect resolution;
- optional external service lookup.

Ports should express system capabilities, not concrete tool names.

## Domain group checkpoints

After completing a pure `Domain` group, pause before moving upward and decide whether a higher layer is justified.

Checklist:

1. The group has enough cohesive behavior to support a use case.
2. The functions are pure and tested.
3. The next layer would compose multiple meaningful rules or expose a system action.
4. No infrastructure dependency is required for the proposed `Application` use case.
5. Ports are introduced only if the next step crosses IO, network, filesystem, browser, parser, AI, OCR, YARA, or external tool boundaries.

Move upward when a use case composes meaningful behavior, not just because one helper exists.

Example:

```text
Domain URL helpers completed -> AnalyzeUrlIndicatorsUseCase may be justified.
One isolated helper added -> continue in Domain unless a real use case needs it.
```

Correct:

```python
class SandboxBrowserPort(Protocol):
    async def capture(self, url: str) -> SandboxResult:
        ...
```

Less appropriate:

```python
class PlaywrightPort(Protocol):
    ...
```

## Adapter design

An adapter should:

- implement a port;
- encapsulate a concrete tool;
- handle technical errors;
- apply timeouts and limits;
- translate external data into internal models;
- be replaceable.

Examples:

```text
PlaywrightSandboxAdapter implements SandboxBrowserPort
OllamaAiAnalysisAdapter implements AiAnalysisPort
TesseractOcrAdapter implements OcrPort
YaraScannerAdapter implements MalwareSignatureScannerPort
```

## Evaluating new modules

When adding a module, decide:

1. which concept belongs to Domain;
2. which use case or port belongs to Application;
3. which adapter belongs to Infrastructure;
4. which entrypoint invokes it;
5. which tests guarantee the boundary.

Example: OCR module.

```text
Domain: extracted text findings and indicators.
Application: OcrPort and use case requesting extraction.
Infrastructure: TesseractOcrAdapter.
Entrypoint: endpoint or analysis flow invoking the use case.
Tests: pure domain tests + use case with mock + adapter with controlled fixture.
```

## Local AI rules

The ADR defines optional local AI with Ollama.

Architecturally:

- Ollama belongs to Infrastructure.
- Application defines an AI port.
- Domain does not know prompts, models, or SDKs.
- If AI is disabled, the flow must continue cleanly.
- AI complements deterministic analysis; it does not replace it.

## Sandbox rules

Playwright/Chromium must remain isolated infrastructure.

Architecturally:

- Domain does not open browsers;
- Application defines the contract;
- Infrastructure implements Playwright;
- Docker Compose isolates the browser;
- the use case receives results, not browser details.

## Docker and service rules

Docker Compose must reflect architectural boundaries:

- `frontend`: React UI;
- `backend`: API and use cases;
- `playwright/browser`: isolated sandbox;
- `ollama`: optional local AI when applicable.

Do not mix responsibilities between services. The backend orchestrates, but the sandbox container must not become part of the domain.

## Bad architecture signals

Review and correct if you detect:

- FastAPI imports in Domain;
- Playwright/Ollama/YARA/OCR imports in Domain;
- endpoints with extensive forensic logic;
- use cases instantiating concrete adapters;
- tests requiring real network for business rules;
- risk logic scattered between frontend and backend;
- external DTOs used as domain entities without a deliberate decision;
- missing ports for replaceable integrations;
- business rules embedded in Docker, scripts, or entrypoints.

## Relationship with other skills

- Use `phishshield-backend` for backend implementation details once the architecture is decided.
- Use `phishshield-security-analysis` when it exists and the focus is concrete forensic analysis logic.
- Use `phishshield-testing` when the focus is testing strategy or test implementation.
- Use `phishshield-devops` when it exists and the focus is CI/CD or deployment.

If a task mixes architecture and implementation, start with this skill and then apply the relevant technical skill.

## Rejection criteria

Reject or redesign a proposal if it:

- requires importing infrastructure from `Domain`;
- makes FastAPI, Playwright, Ollama, YARA, OCR, or parsers dependencies of the core;
- prevents replacing an external tool without touching use cases or domain;
- mixes forensic analysis, HTTP transport, and presentation in the same component;
- turns Docker Compose or scripts into the place for business rules;
- introduces real network access in tests for pure rules;
- explicitly contradicts `doc/ADR.md`.

## Checklist before approving an architectural decision

- [ ] The decision respects `doc/ADR.md`.
- [ ] Dependencies point toward the domain, not away from it.
- [ ] Domain does not depend on frameworks or SDKs.
- [ ] Application defines ports when crossing technical boundaries.
- [ ] Infrastructure implements replaceable adapters.
- [ ] Entrypoints do not contain business rules.
- [ ] Forensic modules remain extensible.
- [ ] The local/self-hosted privacy approach is preserved.
- [ ] There is a testing strategy aligned with the change.
- [ ] The solution avoids accidental complexity.

## Examples

### Initial structure proposal

Correct:

```text
src/
  domain/
  application/
  infrastructure/
    entrypoints/
```

Incorrect:

```text
src/
  app.py
  services.py
  utils.py
```

if endpoints, parsers, risk rules, and external calls are mixed there.

### Endpoint directly calling Playwright

Diagnosis:

```text
This breaks layer separation if the endpoint contains sandbox logic.
```

Correction:

```text
FastAPI -> UseCase -> SandboxBrowserPort -> PlaywrightSandboxAdapter
```

### Homoglyph detection

If it is a pure algorithm:

```text
Domain
```

If it depends on external libraries or IO:

```text
Infrastructure behind a port, while keeping stable types and rules in Domain/Application.
```

## Suggested eval prompts

Use these prompts to check whether the skill guides the agent correctly:

1. `Propose the initial folder structure for PhishShield according to the ADR.`
2. `Add a new OCR module with Tesseract without breaking hexagonal architecture.`
3. `Review this proposal: the FastAPI endpoint opens Playwright directly to capture screenshots.`
4. `Design how to integrate Ollama optionally while respecting ports and adapters.`
5. `Decide where homoglyph detection should live and justify the layer.`

A good answer should consult the ADR, justify layers, define ports/adapters when needed, and detect improper coupling.
