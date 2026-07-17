# Frontend MVP Plan

## Purpose

This document defines the first usable frontend for PhishShield.

Its purpose is to keep the initial React UI focused on the current backend contract while avoiding premature complexity before broader forensic modules or production packaging are introduced.

The current frontend MVP is functionally complete enough to support upload and result inspection. It now uses a wider analyst-workbench layout that separates upload context from analysis output. The next frontend work should focus on UX polish or backend response enrichment when the UI needs additional evidence fields.

---

## Current Scope

The current frontend MVP lets a user:

- select an `.eml` file;
- drag and drop an `.eml` file;
- submit it to the backend through `POST /api/analyze-email`;
- inspect the returned risk level and scores;
- inspect critical-indicator status;
- inspect extracted sender, subject, URLs, attachment names, and authentication results;
- inspect findings grouped by category;
- inspect backend-provided finding explanations;
- inspect finding category counts;
- inspect unique finding codes;
- download a Markdown report for the current analysis result;
- see loading, empty, success, and error states.

---

## Architecture

- Frontend stack: React + TypeScript + Vite.
- Frontend lives in `frontend/`.
- Runtime frontend code lives in `frontend/src/`.
- Frontend tests live in `frontend/tests/`.
- Frontend test setup lives in `frontend/tests/setup.ts`.
- Frontend `.test.ts` and `.test.tsx` files should not be placed inside `frontend/src/`.
- Vite development proxy maps `/api` to `http://127.0.0.1:8000`.
- No backend CORS is required for the current development flow.
- The backend remains runnable without Docker.
- Docker remains optional for frontend and backend development.
- The current UI uses an analyst-workbench layout with a dedicated input/context sidebar and a separate results panel.

---

## Frontend Test Structure

- Runtime frontend code belongs in `frontend/src/`.
- Frontend tests belong in `frontend/tests/`.
- Vitest and React Testing Library setup belongs in `frontend/tests/setup.ts`.
- Do not place `.test.ts` or `.test.tsx` files inside `frontend/src/`.

---

## Current Features

Done:

- Vite React scaffold;
- typed API client for `POST /api/analyze-email`;
- `.eml` file input;
- drag-and-drop upload;
- basic `.eml` validation;
- frontend-specific error messages for backend/network failures;
- risk summary cards;
- extracted evidence rendering for sender, subject, URLs, attachments, and authentication results;
- grouped findings by category;
- backend-provided finding explanations rendered in the findings view;
- finding category counts;
- empty state;
- success state;
- explicit loading, empty, success, and error result states;
- frontend-side Markdown report export based on the current API result;
- extracted `AnalysisResults` component for result rendering;
- wider workbench layout that separates input/context from analysis results;
- Vitest + React Testing Library coverage for the current upload/results flow, organized under `frontend/tests/`;
- frontend test/build job in GitHub Actions.

---

## Explicitly Deferred

These items are intentionally out of scope for the current frontend MVP:

- advanced visual design system;
- Tailwind setup;
- routing;
- persisted analysis history;
- drag-and-drop polish beyond basic support;
- screenshots or browser-evidence rendering;
- frontend Docker image;
- production static hosting strategy;
- deeper analyst guidance such as remediation recommendations;
- richer report export targets such as HTML, PDF, or backend-generated export workflows.

---

## Next Steps

The next recommended frontend group after the workbench layout redesign is realistic fixture-driven polish over the current evidence and explanation model.

Potential mini-steps:

1. Improve result hierarchy and severity visual language inside the current workbench layout.
2. Add dedicated `AnalysisResults` tests if the component grows in complexity.
3. Revisit wording only when backend fixtures reveal confusing analyst-facing phrasing.
4. Keep new frontend tests under `frontend/tests/` as a repository rule.

---

## Completion Criteria

This frontend MVP phase is considered complete when:

- the upload flow works;
- error handling is clear;
- analysis results are readable;
- frontend tests pass;
- frontend build passes;
- CI runs frontend tests and build.
