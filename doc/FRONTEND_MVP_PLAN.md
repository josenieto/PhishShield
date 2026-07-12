# Frontend MVP Plan

## Purpose

This document defines the first usable frontend for PhishShield.

Its purpose is to keep the initial React UI focused on the current backend contract while avoiding premature complexity before broader forensic modules or production packaging are introduced.

---

## Current Scope

The current frontend MVP lets a user:

- select an `.eml` file;
- drag and drop an `.eml` file;
- submit it to the backend through `POST /api/analyze-email`;
- inspect the returned risk level and scores;
- inspect critical-indicator status;
- inspect findings grouped by category;
- inspect finding category counts;
- inspect unique finding codes;
- see loading, empty, success, and error states.

---

## Architecture

- Frontend stack: React + TypeScript + Vite.
- Frontend lives in `frontend/`.
- Vite development proxy maps `/api` to `http://127.0.0.1:8000`.
- No backend CORS is required for the current development flow.
- The backend remains runnable without Docker.
- Docker remains optional for frontend and backend development.

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
- grouped findings by category;
- finding category counts;
- empty state;
- success state;
- Vitest + React Testing Library coverage for the current upload/results flow;
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
- broader API response enrichment for full extracted email details.

---

## Next Steps

The next recommended group after this MVP is frontend UX polish.

Potential mini-steps:

1. Extract an `AnalysisResults` component.
2. Add dedicated tests for grouped findings and category counts.
3. Improve result hierarchy and severity visual language.
4. Revisit backend API enrichment if the frontend needs more evidence fields.

---

## Completion Criteria

This frontend MVP phase is considered complete when:

- the upload flow works;
- error handling is clear;
- analysis results are readable;
- frontend tests pass;
- frontend build passes;
- CI runs frontend tests and build.
