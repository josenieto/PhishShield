---
name: phishshield-frontend
description: Specialized guidance for PhishShield frontend work with React, TypeScript, Vite, upload flows, API result rendering, frontend testing, and forensic UX. Use this skill whenever implementing, reviewing, or planning frontend UI, upload interactions, risk and finding presentation, Vite proxy behavior, frontend tests, or visual polish for the phishing analysis dashboard. Also use it when deciding whether to add Tailwind, routing, state management, CORS, Playwright evidence UI, or frontend Docker packaging.
---

# phishshield-frontend

## Purpose

Help AI agents build and refine the **PhishShield** frontend while keeping it aligned with the backend contract, the repository ADR, and the current MVP scope.

The frontend exists to make backend findings understandable and actionable for a human analyst. It should prioritize clarity, trust, and readable forensic evidence over generic dashboard styling.

## References to consult

Before making relevant frontend changes, read:

- `AGENT.md`
- `docs/ADR.md`
- `docs/API.md`
- `docs/FRONTEND_MVP_PLAN.md`
- `.skills/README.md`

If this skill conflicts with `docs/ADR.md`, the ADR takes precedence.

## Working process

When this skill triggers:

1. Confirm whether the task is frontend implementation, frontend UX polish, or a frontend architecture decision.
2. If there is uncertainty about boundaries between frontend, backend, or infrastructure, apply `phishshield-architecture` first.
3. Treat the current backend API contract as the source of truth unless the task explicitly changes the contract.
4. Prefer the smallest useful UI increment.
5. Keep the current frontend MVP in `frontend/` simple and testable.
6. Preserve native-first development. Docker may support the frontend later, but it must not become the only development path without a deliberate decision.
7. Add or update frontend tests when the user-visible behavior changes.
8. Finish with a short check against the frontend checklist.

The goal is to produce frontend changes that are easy to understand, easy to test, and consistent with the current backend evidence model.

## When to use this skill

Use this skill for tasks related to:

- React + TypeScript + Vite implementation;
- frontend file upload flows;
- drag-and-drop interactions;
- rendering backend analysis results;
- frontend UX for findings, severity, categories, and risk;
- Vite development proxy decisions;
- frontend state and component structure;
- frontend test design with Vitest and React Testing Library;
- frontend build and CI behavior;
- deciding whether CORS is needed in development;
- deciding whether Tailwind, routing, or state management should be introduced;
- deciding whether frontend Docker packaging is justified.

Do not use this skill for purely backend implementation unless the frontend depends on a backend API contract change. In that case, coordinate with `phishshield-backend` or `phishshield-architecture`.

## Expected response shape

When using this skill, structure the answer briefly and practically:

```text
1. Frontend objective
2. Backend contract assumptions
3. Proposed UI or interaction change
4. State and component impact
5. Frontend tests to add or update
6. UX risks avoided
7. Next smallest useful step
```

## Frontend architecture rules

### 1. Respect the current frontend location and tooling

- Keep the frontend in `frontend/`.
- Use React + TypeScript + Vite.
- Use the current Vite proxy for local development:

```text
/api -> http://127.0.0.1:8000
```

- Do not introduce CORS configuration in the backend for local development if the Vite proxy already solves the problem.

### 2. Preserve native-first development

The backend and frontend must remain runnable without Docker in development.

Use Docker as an optional runtime and packaging path, not as a mandatory development prerequisite, unless the active roadmap group explicitly changes that constraint.

### 3. Keep the frontend contract-driven

The frontend should consume backend responses as they exist now, not invent speculative fields.

Current important backend response groups:

- `finding_codes`
- `unique_finding_codes`
- `finding_summary`
- `risk_score`

If the UI needs additional evidence fields, propose API enrichment explicitly instead of silently inventing frontend-only placeholders.

### 4. Prioritize forensic clarity over generic UI patterns

The frontend is not a marketing site. It is a forensic analysis interface.

Prefer:

- visible risk summary;
- readable severity hierarchy;
- grouped findings by category;
- critical-indicator visibility;
- explicit empty, loading, success, and error states;
- stable visual language.

Avoid:

- decorative complexity without analytical value;
- hiding raw indicator codes entirely;
- ambiguous labels;
- generic “AI dashboard” aesthetics that reduce trust.

### 5. Do not introduce broad frontend infrastructure prematurely

Do not add these by default unless the current task clearly justifies them:

- Tailwind;
- React Router;
- global state managers;
- design system packages;
- frontend Docker image;
- screenshot or browser evidence UI;
- persisted frontend history.

The default preference is to keep the frontend small and direct until the MVP interaction becomes stable.

## UX rules

### 1. Show the most important signal first

The first meaningful result a user should notice is risk.

Prioritize:

- `risk_score.risk_level`
- `risk_score.raw_score`
- `risk_score.has_critical_indicators`

Then show grouped findings and evidence summaries.

### 2. Keep category and severity readable

Use the backend grouping and ordering as much as possible.

Reasonable result structure:

- summary cards;
- grouped findings by category;
- category counts;
- unique indicator codes.

### 3. Handle user mistakes clearly

For upload UX, the user should receive explicit messages for:

- missing file;
- invalid file type;
- oversized upload;
- backend analysis failure;
- backend not reachable.

Do not collapse everything into a generic error toast.

### 4. Keep drag-and-drop accessible

If drag-and-drop exists, keep the ordinary file input too. Do not make drag-and-drop the only upload path.

## Testing rules

Frontend behavior changes should use:

- **Vitest**
- **React Testing Library**
- **jsdom**

Prefer tests for:

- upload interactions;
- invalid file handling;
- API client error mapping;
- empty state;
- success state;
- grouped findings rendering;
- category count rendering.

Avoid overly brittle snapshot tests.

When a visual or structural refactor makes testing easier, prefer extracting a component rather than writing fragile selectors against a large page component.

## Current MVP checklist

Before finishing a frontend task, check:

- Does the change preserve the current backend contract?
- Is the upload flow still readable and accessible?
- Are empty, loading, success, and error states still clear?
- Are risk and findings still easy to understand?
- Were frontend tests added or updated if user-visible behavior changed?
- Does `npm run build` still pass?
- Does the change avoid introducing unnecessary frontend infrastructure?

## Recommended next skills

- Use `phishshield-architecture` if the frontend request really requires an API contract or layering decision.
- Use `phishshield-testing` if the main challenge is TDD strategy or test design.
- Use `phishshield-backend` if the task requires backend API enrichment to support the UI.
