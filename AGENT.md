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

The system analyzes, among other aspects:

- email headers and sender identity,
- links and homoglyph attacks,
- safe browsing sandbox results,
- PDF and Office attachments,
- OCR and image metadata,
- optional local AI-assisted explanations when enabled.

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
- **Testing:** Pytest
- **CI/CD:** GitHub Actions

---

## Functional modules

The main modules described in the ADR are:

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

---

## Working rules for AI agents

### 1. Review the ADR before relevant changes

If a change affects architecture, contracts, modules, or deployment, consult `doc/ADR.md` first.

### 2. Respect layer separation

- Do not move business rules into adapters.
- Do not contaminate the domain with SDKs, frameworks, network, filesystem, or runtime details.
- Keep use cases coordinated through ports, not concrete implementations.

### 3. Prioritize security and privacy

PhishShield is a defensive security tool.  
Every change must avoid unnecessary exposure of sensitive data and preserve the local/self-hosted approach.

### 4. Keep typing and validation explicit

Use explicit models and validation consistently with the project stack, especially in backend code and API contracts.

### 5. Favor extensibility

New integrations must be designed so they can be replaced without breaking the core system.

### 6. Add or update tests

If a change modifies observable behavior, add or update tests in the appropriate layer.

### 7. Avoid accidental complexity

Prefer clear, modular solutions aligned with the existing ADR.

---

## Engineering journey documentation

The project maintains an engineering journey document at:

- `doc/ENGINEERING_JOURNEY.md`

Agents must update this document whenever a relevant engineering step occurs.

Relevant steps include:

- completing a TDD cycle;
- making an architectural decision;
- deciding not to move up a layer;
- creating a new domain function group;
- adding a new port;
- adding a new adapter;
- introducing a new use case;
- changing folder architecture;
- adding a new project skill;
- creating or changing a testing strategy;
- making an important rejection decision.

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

When a step changes architecture flow or layer progression, update the Mermaid diagrams in `doc/ENGINEERING_JOURNEY.md`.

Do not over-document every small code edit. Document meaningful engineering steps that explain how the project evolves.

---

## What an agent must do before editing

Minimum checklist:

- read `doc/ADR.md`,
- identify the affected layer,
- locate the impacted contract or module,
- check whether tests are required,
- keep consistency with Docker, FastAPI, React, and existing adapters.

---

## Project skills

Project-specific skills are organized in:

- `.skills/`

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