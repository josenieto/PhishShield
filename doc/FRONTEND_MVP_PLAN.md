# Frontend MVP Plan

## Purpose

This document defines the first usable frontend for PhishShield.

Its purpose is to keep the initial React UI focused on the current backend contract while avoiding premature complexity before broader forensic modules or production packaging are introduced.

The current frontend MVP is functionally complete enough to support upload, result inspection, and the initial report/export v2 actions. It now uses a wider analyst-workbench layout that separates upload context from analysis output. The next frontend work should focus on analyst polish or backend response enrichment when the UI needs additional evidence fields.

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
- download or copy a Markdown report for the current analysis result;
- preview the generated Markdown report before copying or downloading it;
- download the structured analysis result as JSON;
- download the generated report as HTML;
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
- clipboard copy action for the generated Markdown report;
- Markdown report preview inside the analysis results view;
- frontend-side JSON export for the current API result;
- frontend-side HTML export for the generated report;
- grouped report and export actions in a dedicated analysis panel;
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

## Analyst Polish Status

The analyst polish milestone is complete. The current workbench now includes:

- risk and severity hierarchy for `LOW`, `MEDIUM`, `HIGH`, and `CRITICAL` results;
- critical-indicator emphasis and category-level highest-severity context;
- prioritized sender, subject, URL, attachment, and authentication evidence;
- explicit advisory, completed, failed, and not-configured model assessment states;
- responsive layouts and wrapping for long URLs, filenames, signals, and finding codes;
- focused frontend coverage for result rendering and export flows.

The frontend remains intentionally small and contract-driven. No routing, persisted
history, global state manager, frontend Docker image, or screenshot evidence UI was
introduced by this milestone.

## Next Steps

Frontend work should now be maintenance-driven rather than a new broad roadmap group.
Revisit the UI when backend fixtures expose confusing analyst-facing wording or when
the backend contract gains evidence with clear analyst value.

The next primary project group is fixture-driven parser and runtime polish in the
backend. Keep new frontend tests under `frontend/tests/` as a repository rule.

---

## Completion Criteria

This frontend MVP phase is considered complete when:

- the upload flow works;
- error handling is clear;
- analysis results are readable;
- frontend tests pass;
- frontend build passes;
- CI runs frontend tests and build.
