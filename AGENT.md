# AGENT.md

## Purpose

This file guides any AI agent working on this repository.
Its role is to provide a concise operational guide: what this software project is, how it is structured, and which rules every change must follow.

This document does **not** replace the official architectural design. The main source of truth is:

- `doc/ADR.md`

If this file conflicts with the ADR, **the ADR takes precedence**.

---

## Repository language policy

Everything committed to this repository must be written in English.

This includes:

- documentation,
- Markdown files,
- skills,
- eval prompts,
- commit messages,
- GitHub issues,
- GitHub Project items,
- branch names,
- code identifiers,
- comments,
- test names,
- fixtures,
- configuration examples.

Do not add Spanish text to repository files.

The only acceptable exceptions are explicit test samples or fixtures where multilingual content is the subject under test. Those exceptions must be clear from the test or fixture context.

---

## Project

**PhishShield** is a defensive, local, self-hosted, open-source tool for forensic analysis of `.eml` email files.

Its goal is to detect modern phishing indicators without depending on third-party cloud services for the main analysis workflow, preserving privacy, traceability, and technical extensibility.

The full target product analyzes, among other aspects:

- email headers and sender identity,
- links and homoglyph attacks,
- safe browsing sandbox results,
- PDF and Office attachments,
- OCR and image metadata,
- optional local AI-assisted explanations when enabled.

The current implemented scope is tracked in:

- `doc/BACKEND_EVOLUTION_PLAN.md`
- `doc/FRONTEND_MVP_PLAN.md`

---

## Mandatory architectural reference

Before modifying code, read:

- `doc/ADR.md`

The project follows a **Hexagonal Architecture** inside a **modular monolith**.
Design decisions and boundaries between layers must respect that architecture.

### Expected layers

- **Domain**
  Pure models and business rules with no infrastructure dependencies.

- **Application**
  Use cases and ports defining contracts.

- **Infrastructure**
  Technical adapters, frameworks, parsers, integrations, and entrypoints.

### Main rule

An AI agent **must not introduce infrastructure dependencies into the domain**.
Every external integration must be encapsulated behind ports and adapters.

---

## Main stack

According to the ADR, the project's main technical stack is:

- **Backend:** Python + FastAPI
- **Frontend:** React + TypeScript + Vite
- **Deployment:** Docker + Docker Compose
- **Browsing sandbox:** Playwright in an isolated container
- **Optional local AI:** Ollama
- **Testing:** Pytest for backend, Vitest + React Testing Library for frontend
- **CI/CD:** GitHub Actions

Current active stack in the repository:

- Python + FastAPI backend
- React + TypeScript + Vite frontend
- backend Docker runtime and Compose wiring
- GitHub Actions for backend tests, frontend tests/build, and Docker health smoke

Still deferred unless explicitly selected as the current roadmap group:

- Playwright browser sandbox
- Ollama or other AI integrations
- YARA
- OCR
- PDF and Office forensic parsing beyond current metadata/filename scope

---

## Functional modules

The ADR describes these target capability groups:

1. **Headers and identity**
   - sender extraction, subject extraction, and SPF/DKIM/DMARC validation.

2. **Links and homoglyph attacks**
   - IDN detection, Punycode normalization, and passive short URL resolution.

3. **Safe browsing sandbox**
   - visual capture and page title extraction through an isolated browser.

4. **Attachments**
   - PDF analysis, Office analysis, macros, hashes, and YARA rules.

5. **Images**
   - OCR with Tesseract and EXIF metadata extraction.

6. **Local AI**
   - complementary social engineering analysis and natural language explanation, controlled by configuration.

These groups are architectural targets, not a statement that every module is implemented today. Use the backend and frontend plan documents for current status.

---

## Working rules for AI agents

### 1. Review the ADR before relevant changes

If a change affects architecture, contracts, modules, or deployment, consult `doc/ADR.md` first.

### 2. Respect layer separation

- Do not move business rules into adapters.
- Do not contaminate the domain with SDKs, frameworks, network, filesystem, or runtime details.
- Keep use cases coordinated through ports, not concrete implementations.
- Keep extraction from external formats in infrastructure adapters or behind application ports. Domain services analyze already extracted values; they must not extract URLs, attachments, authentication results, hashes, text, or metadata from `.eml`, HTML, PDFs, Office files, OCR output, byte streams, filesystem paths, network responses, or external tool output.

### 3. Prioritize security and privacy

PhishShield is a defensive security tool.
Every change must avoid unnecessary exposure of sensitive data and preserve the local/self-hosted approach.

### 4. Keep typing and validation explicit

Use explicit models and validation consistently with the project stack, especially in backend code and API contracts.

### 5. Favor extensibility

New integrations must be designed so they can be replaced without breaking the core system.

### 6. Add or update tests

If a change modifies observable behavior, add or update tests in the appropriate layer.

Testing distribution guideline:

- treat test distribution as a health signal, not a hard quota;
- prefer most backend behavioral coverage in `Domain`, because it is the cheapest and most deterministic layer to test;
- use `Application` tests to validate orchestration, ports, deduplication, scoring composition, and use case contracts;
- use `Infrastructure` and API tests to validate adapters, parsers, framework boundaries, configuration, and error handling;
- keep end-to-end and smoke coverage small, stable, and focused on critical user journeys.

Current target distribution guideline for PhishShield:

- `Domain`: 55-60%;
- `Application`: 20-25%;
- `Infrastructure/API`: 10-15%;
- `E2E/smoke`: 5-10%.

These percentages are based on feedback speed, maintenance cost, and diagnostic value. Do not add artificial tests just to match the ratio.

Frontend repository structure rule:

- production frontend code lives under `frontend/src/`;
- frontend tests live under `frontend/tests/`;
- frontend test setup files also live under `frontend/tests/`;
- do not place frontend `.test.ts` or `.test.tsx` files inside `frontend/src/`.

### 7. Avoid accidental complexity

Prefer clear, modular solutions aligned with the existing ADR.

### 8. Respect the current layer progression

The ADR defines the target stack. Do not introduce a new infrastructure family until the active roadmap group requires it.

Already introduced infrastructure such as FastAPI, React/Vite, Docker, Docker Compose, and GitHub Actions may be extended when working inside their active roadmap group.

Playwright, Ollama, YARA, OCR, and broader PDF or Office parsing remain deferred unless they become the explicit focus of the current group.

After completing a pure `Domain` group, run an architectural checkpoint before moving upward to `Application`, `Infrastructure`, or entrypoints.

---

## Development workflow

For behavior changes, use the smallest useful increment and follow this workflow:

1. Check repository status before editing.
2. Define the smallest behavior increment.
3. **RED:** add the failing test and confirm the expected failure.
4. **GREEN:** implement the minimum code required to pass.
5. **REFACTOR:** review whether cleanup improves clarity without changing behavior.
6. **VERIFY:** run affected tests and the full suite when it is still cheap.
7. Update documentation only when the step is meaningful.
8. Stop before committing unless the user explicitly asks the agent to commit.

The refactor phase is mandatory as a review step, but code changes are optional. If no cleanup is useful, state `Refactor not needed.`

### project knowledge graph refresh policy

project knowledge graph is an architectural snapshot and navigation aid, not a per-change build artifact.

Regenerate project knowledge graph only after:

- adding or removing a major module, layer, port, adapter, or entrypoint;
- changing dependencies between Domain, Application, Infrastructure, or Entrypoints;
- significantly reorganizing folders or frontend component composition;
- changing the main analysis flow;
- introducing a new infrastructure family;
- closing a milestone or making another structural architectural change.

Do not regenerate project knowledge graph for:

- routine implementation changes;
- localized parser fixes or tests;
- styling, copy, or responsive adjustments;
- minor documentation changes;
- fixture-backed scoring calibration;
- routine CI, guardrail, or local configuration changes.

Use the existing `project knowledge graph-out/` snapshot between structural refreshes. If the answer
to “would this change the project map for a new contributor?” is no, do not regenerate
project knowledge graph. When the answer is yes, refresh it at the relevant architectural milestone.

The repository also maintains local `pre-commit` guardrails for hygiene, Domain/Application boundary protection, commit-message validation, and scoring-sensitive change checks. Keep `AGENT.md`, `.pre-commit-config.yaml`, and the guard scripts under `scripts/` aligned when workflow expectations change.

The `pre-commit` configuration is versioned, but hook installation is per clone. Treat `git commit --no-verify` as an intentional bypass of local protections; CI remains the shared enforcement layer.

Full-suite verification trigger policy:

- run `python -m pytest` before marking work complete when a change touches shared value objects, Domain finding definitions, Application result models, API response schemas, parser adapters, or other contracts reused across multiple backend layers;
- run frontend verification with `cmd /c npm run test` and `cmd /c npm run build` when a change touches frontend API types, shared UI result models, or frontend rendering contracts;
- partial test scopes are useful during development, but they are not sufficient as final verification for cross-layer contract changes.

### Commit message format

Use this format when proposing or creating commits:

```text
type(scope): Action summary.

- Body bullet with uppercase initial and final period.
- Another body bullet with uppercase initial and final period.
```

Expectations:

- Use a one-line summary plus a blank line plus body bullets for non-trivial commits.
- Do not propose summary-only commit messages for `feat`, `fix`, `refactor`, `test`, or meaningful `docs` changes unless the change is truly trivial.
- Keep the summary concise and action-oriented, with an uppercase initial and final period.
- Keep each body bullet concise, with an uppercase initial and final period.
- Match the repository's recent commit style when proposing commit text.

Example:

```text
feat(domain): Add embedded URL credential detection.

- Add pure URL embedded credential detection.
- Use standard library URL parsing without network or DNS access.
```

Additional example:

```text
feat(frontend): Add Markdown analysis report export.

- Generate a frontend-side Markdown report from the current analysis result.
- Add a download action to the completed analysis state.
- Cover report generation and export UI behavior with frontend tests.
```

---

## Engineering journey documentation

The project maintains an engineering journey document at:

- `doc/ENGINEERING_JOURNEY.md`

Agents should update this document for meaningful milestones, architectural decisions, strategy shifts, or phase closures.

Relevant steps include:

- completing a meaningful TDD cycle;
- making an architectural decision;
- deciding not to move up a layer;
- creating a new domain function group;
- completing a domain function group checkpoint;
- adding a new port;
- adding a new adapter;
- introducing a new use case;
- changing folder architecture;
- adding a new project skill;
- creating or changing a testing strategy;
- making an important rejection decision.
- closing a major roadmap group.

Use this entry format:

```md
## YYYY-MM-DD - [Short title]

Type: TDD | Architecture | Testing | Skill | Documentation | Refactor
Layer: Domain | Application | Infrastructure | Entrypoint | Cross-cutting
Status: Proposed | Done | Rejected | Deferred

### Context

Why this step happened.

### Decision

What was decided or completed.

### Files changed

- ...

### Tests

Command:

```bash
...
```

Result:

```text
...
```

### Next step

...
```

Do not use Markdown hard-break trailing spaces on the `Type`, `Layer`, or `Status` lines in `doc/ENGINEERING_JOURNEY.md`. The trailing-whitespace hook strips them and will abort the commit so the fixed file can be staged again.

When a step changes architecture flow or layer progression, update the Mermaid diagrams in `doc/ENGINEERING_JOURNEY.md` if those diagrams exist and the change is still meaningful.

Do not over-document every small code edit. Prefer milestone-oriented entries over per-helper noise.

For small helpers inside the same function group, prefer concise grouped entries unless the helper introduces a notable architectural or testing decision.

---

## What an agent must do before editing

Minimum checklist:

- read `doc/ADR.md`,
- read the current roadmap document for the active group when relevant,
- identify the affected layer,
- locate the impacted contract or module,
- check whether tests are required,
- check whether the change should stay in the current layer,
- keep consistency with the ADR target stack without introducing deferred infrastructure prematurely.

---

## Project skills

Project-authored skill definitions and evals are organized in:

- `.skills/`

Installed skills available to the agent runtime are organized under `.agents/skills/` when they are installed for this project. A skill definition in `.skills/` is not automatically runtime-available unless it is registered or installed through the active agent configuration.

The official Anthropic `skill-creator` skill is installed in the project through the `skills` CLI and is available at:

- `.agents/skills/skill-creator/`

Command used:

```bash
npx skills add anthropics/skills --skill skill-creator --yes
```

It is used to create, improve, and evaluate PhishShield-specific skills.

### Mandatory rule for creating new skills

Every new project skill must be created using the official skill as the model:

- `.agents/skills/skill-creator/`

The agent must apply that workflow before writing a skill:

1. capture the skill intent,
2. define when the skill should trigger,
3. write `SKILL.md` with `name` and `description` frontmatter,
4. keep the skill actionable, specific, and aligned with PhishShield,
5. create initial evals when the skill is objectively testable,
6. verify alignment with `AGENT.md` and `doc/ADR.md`,
7. update `.skills/README.md`.

Do not create skills without following this process.

### Planned skills

Initial folders are prepared, and skills are defined progressively with `skill-creator`.

- `phishshield-architecture`
  Architecture decisions aligned with the ADR.

- `phishshield-backend`
  FastAPI, use cases, ports, and adapters.

- `phishshield-frontend`
  React, TypeScript, Vite, and forensic dashboard UI.

- `phishshield-security-analysis`
  Link analysis, attachment analysis, OCR, and forensic indicators.

- `phishshield-testing`
  Unit and integration testing with Pytest and mocks.

> Until a skill exists, use this file, `.skills/README.md`, and `doc/ADR.md` as the main references.

---

## Final rule

If a decision is unclear:

1. follow `doc/ADR.md` first,
2. preserve hexagonal architecture,
3. prioritize security, privacy, and maintainability.
