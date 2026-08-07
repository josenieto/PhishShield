# Architectural Decision Record (ADR): PhishShield Target Architecture

## 1. Context and Problem

Modern phishing bypasses traditional filters through social engineering techniques, homoglyph attacks using Unicode/Punycode lookalike characters, and hidden payloads in attachments such as Office macros, links inside PDFs, and text embedded in images.

Current enterprise solutions are often proprietary, expensive, and require sending sensitive data to third-party clouds, which weakens privacy. PhishShield needs to be a defensive, local, self-hosted, open-source, and extensible tool for visual and safe forensic analysis of `.eml` email files.

This ADR describes the target architecture and long-term capability set.

The current implemented MVP scope is tracked separately in:

- `docs/BACKEND_EVOLUTION_PLAN.md`
- `docs/FRONTEND_MVP_PLAN.md`

---

## 2. Adopted Technical Decisions

### 2.1 Software Architecture: Hexagonal Modular Monolith

- **Decision:** Implement **Hexagonal Architecture (Ports and Adapters)** combined with Clean Architecture in a single modular repository.
- **Rationale:** This strictly separates cybersecurity business rules in Domain/Application from external technical tools in Infrastructure. It allows analysis libraries or web frameworks to be replaced in the future without changing the system core.
- **Layer structure:**
  - `Domain`: pure data models such as `Email` and `AnalysisResult`, dependency-free rules, and pure algorithms such as homoglyph detection.
  - `Application`: use cases and `Ports`, which are abstract interfaces defining contracts, for example `LinkAnalyzerPort`.
  - `Infrastructure`: concrete technical `Adapters`, such as FastAPI, Playwright, native parsers, and API `Entrypoints`.

### 2.2 Main Technology Stack

- **Backend:** **Python + FastAPI**
  - **Rationale:** Python is a standard ecosystem for cybersecurity and has mature forensic libraries. FastAPI provides strong typing with Pydantic and native asynchronous performance for concurrent analysis workflows.
- **Frontend:** **React + TypeScript + Vite**
  - **Rationale:** This enables a modern SPA for drag-and-drop file upload and dashboard visualization of forensic reports with Tailwind CSS.

### 2.3 Deployment and Distribution Strategy

- **Model:** **Local self-hosted web application** distributed through **Docker and Docker Compose**.
- **Target container architecture:**
  1. `Frontend`: serves the React web UI on port 3000.
  2. `Backend`: exposes the FastAPI API that runs security rules on port 8000.
  3. `Playwright/Browser`: runs an isolated Chromium browser container to capture screenshots of links without putting the user's host system at risk.

- **Current MVP runtime scope:**
  1. `Backend`: Dockerfile and Compose runtime are implemented and validated.
  2. `Frontend`: Vite development flow is implemented. Frontend containerization is still deferred.
  3. `Playwright/Browser`: deferred.

### 2.4 CLI and CI/CD Automation Direction

- **Decision direction:** PhishShield should eventually expose deterministic email analysis through a command-line entrypoint so it can be used from local scripts and CI/CD pipelines in addition to the web application.
- **Architecture:** the CLI must reuse existing `Application` use cases and contracts. It must not duplicate parsing, scoring, finding, or risk logic outside the application flow.
- **Initial interface:** accept `.eml` file paths and, when practical, standard input; produce human-readable text and structured JSON output; and expose stable exit codes for configurable risk thresholds.
- **Future formats:** batch/JSONL, Markdown, and SARIF may be added when a concrete automation or security-platform workflow justifies them.
- **Deterministic-first rule:** the deterministic result remains authoritative for CLI and CI decisions. Model assessment remains optional, advisory, disabled by default, and must not become a default CI gate.
- **Safety wording:** CLI and CI output represents deterministic phishing triage signals, not a malware verdict or a replacement for broader security controls.

---

## 3. Forensic Analysis Modules

### 3.1 Headers and Identity Module

- Performs static analysis of the raw `.eml` source.
- Extracts sender information and subject.
- Validates global authentication signals: **SPF** for authorized sender server, **DKIM** for message integrity, and **DMARC** for domain policy alignment.

### 3.2 Links and Homoglyph Attacks Module

- Detects visual traps where a domain imitates a legitimate one using characters from other alphabets, for example a Cyrillic `о` inside `microsoft.com`.
- Converts links to their real network representation in **Punycode** (`xn--...`) using Python's `idna` ecosystem where appropriate.
- Resolves shortened links, for example bit.ly, through passive HTTP `HEAD` requests to discover the real destination before analysis.

### 3.3 Safe Browsing Sandbox Module

- Receives URLs from the email and opens them in an automated invisible browser.
- Uses strict security configuration: disables automatic downloads and blocks persistent cookies.
- Captures a static screenshot of the destination page and extracts the tab title so the analyst can visually check whether it clones a bank or real service.

### 3.4 Attachment Module

- **PDF files (`pdfminer` / `PyPDF2`):** automatically extracts hidden links inside documents and sends them to the sandbox module.
- **Office files (Word, Excel):** uses specialized tooling such as **`oletools`** to scan for hidden VBA macros or dangerous automatic scripts.
- **Hash calculation:** generates a SHA-256 hash for each attachment to allow optional checks against global malware databases, for example VirusTotal.
- **YARA rules:** integrates `yara-python` to scan email bodies and attachments using industry-standard signatures.

### 3.5 Images and Visual Content Module

- **OCR engine (Tesseract):** uses `pytesseract` to extract and read text embedded inside email images, preventing attackers from bypassing text filters by using image-only content.
- **EXIF metadata:** extracts hidden information from attached images, such as camera, editing software, and coordinates when present, for forensic purposes.

---

## 4. Future Model-Assisted Analysis

This section describes a deferred target capability. It is not part of the current implemented MVP.

### 4.1 Project-Owned Local Inference Direction

- **Decision direction:** future model-assisted analysis should use a PhishShield-owned model artifact executed inside the project runtime rather than requiring users to install an external AI runtime such as Ollama.
- **User expectation:** the user should not need to install or operate a separate local AI service to obtain the first useful model-assisted assessment flow.
- **Planned endpoint strategy:** future model-assisted analysis should be exposed through a separate endpoint and should assess the original raw email in parallel with the deterministic branch instead of replacing the existing `/analyze-email` flow.

### 4.2 Candidate Implementation Evolution

- **Training and evaluation phase:** the project should first identify acceptable public phishing-email datasets, evaluate their licenses and quality, and define a training/evaluation strategy before choosing a runtime format.
- **Embedded local inference target:** a later version may export a selected classifier model, for example an ONNX artifact derived from a lightweight encoder or classifier, and execute it directly in the backend runtime.
- **Advantage:** this keeps inference self-contained inside PhishShield, avoids external runtime installation requirements, and preserves local privacy guarantees.

### 4.3 Experimental ML Baseline Candidate

- **Decision:** the current experimental ML baseline candidate is a `TF-IDF + Logistic Regression` classifier trained with:
  - the prepared `Phishing Email Detection` dataset;
  - synthetic benign notification calibration data with `600` generated samples;
  - synthetic suspicious notification-style lure calibration data with `600` generated samples.
- **Status:** this is an experimental baseline candidate, not a production model and not yet an inference artifact.
- **Evidence:** on the expanded `32` fixture PhishShield holdout, this candidate produced:

```text
accuracy: 0.8750
false_positive_benign: 3
false_negative_suspicious: 1
```

- **Rationale:** this is the first evaluated candidate that improves overall holdout accuracy and reduces benign false positives while keeping suspicious false negatives low.
- **Rejected or deferred alternatives:**

| Experiment | Holdout size | Accuracy | False positive benign | False negative suspicious | Decision |
|---|---:|---:|---:|---:|---|
| SpamAssassin-only baseline | `10` | `0.4000` | `5` | `1` | Rejected: generic spam signal did not transfer to phishing quality. |
| Fraudulent E-mail Corpus baseline | `10` | `0.4000` | `1` | `5` | Rejected: 419 fraud language reduced benign false positives but lost phishing recall. |
| Phishing Email Detection baseline | `16` | `0.6250` | `6` | `0` | Partial: good suspicious recall, poor benign calibration. |
| Threshold sweep | `16` | no improvement | - | - | Rejected: simple thresholding did not solve benign false positives. |
| SpamAssassin `hard_ham` calibration | `16` | `0.6250` | `6` | `0` | Rejected: difficult ham did not improve notification-like benign calibration. |
| Enron capped sample | `16` | `0.5625` | `6` | `1` | Rejected: narrow sample worsened holdout. |
| Enron source-diverse sample | `16` | `0.6250` | `6` | `0` | Deferred: generic business email did not improve the current false-positive family. |
| Synthetic benign notifications `120` | `16` | `0.6250` | `2` | `4` | Partial: reduced benign false positives but over-calibrated toward benign. |
| Synthetic benign notifications `600` | `16` | `0.5625` | `1` | `6` | Rejected: over-calibrated toward benign. |
| Balanced synthetic notifications `600/600` | `16` | `0.8125` | `2` | `1` | Promising. |
| Balanced synthetic notifications `600/600` | `32` | `0.8750` | `3` | `1` | Current experimental candidate. |

- **Limitations:**
  - the holdout is still small;
  - the candidate depends partly on synthetic calibration data;
  - no non-synthetic notification-style validation source has confirmed the result yet;
  - no model artifact has been exported;
  - no runtime inference adapter is enabled;
  - deterministic analysis remains the authoritative result path.
- **Architectural consequence:** model artifact export, model-card metadata, and local inference adapter work may proceed only as explicitly experimental follow-up work. Product-facing inference remains deferred until additional non-synthetic validation and larger holdout coverage support the candidate.

### 4.4 Experimental Local Inference Adapter Boundary

- **Decision:** the first runtime integration step for the selected candidate is an experimental sklearn adapter, disabled by default and enabled only through explicit local artifact configuration.
- **Planned adapter:** `SklearnModelAssessmentAdapter` in Infrastructure.
- **Configuration direction:** use environment-driven paths such as `PHISHSHIELD_MODEL_ASSESSMENT_ENABLED`, `PHISHSHIELD_MODEL_ARTIFACT_PATH`, and `PHISHSHIELD_MODEL_METADATA_PATH`.
- **Artifact policy:** model artifacts and metadata remain outside Git. The current exported candidate artifact is experimental and must not be treated as a release asset.
- **Runtime behavior:** when not configured, the model branch returns `not_configured`; when configured, it returns advisory `ModelAssessment` output through the existing separate model-assessment endpoint.
- **Architectural constraint:** deterministic findings, evidence, explanations, and risk scoring remain authoritative. Model output must not alter deterministic results in this phase.
- **Failure policy:** artifact load, metadata parse, preprocessing, and prediction failures must return a model-branch failure without breaking deterministic analysis.

### 4.5 Scope-Aware Advisory Inference

- **Decision:** the advisory branch uses a deterministic, auditable scope/family gate before invoking the experimental binary classifier.
- **Covered families:** account, MFA/security, cloud/document sharing, billing/invoices, support, HR, vendor portals, and newsletter/account preferences.
- **Out-of-scope behavior:** generic spam, 419 fraud, mass marketing, personal email, generic malware delivery, URL-only inputs, non-English messages, and unknown campaign types return advisory `inconclusive` without invoking the binary classifier.
- **Separation:** scope membership and binary benign/suspicious classification are distinct decisions. A high binary probability is not evidence of scope membership.
- **Future training:** the gate and binary adapter boundaries remain replaceable. Future authorized external or corporate datasets may train a gate or family-specific classifier after explicit role assignment, provenance/licensing review, deduplication, and independent family-level evaluation.
- **Authority:** the deterministic analysis path remains authoritative and model scope or output cannot alter deterministic findings, evidence, or `risk_score`.

---

## 5. Quality Strategy and Repository Lifecycle

- **Testing:** backend behavior is validated with **Pytest**. Frontend behavior is validated with **Vitest** and **React Testing Library**. Integration tests cover parser, API, and runtime-focused flows. Network-dependent capabilities should be isolated behind ports and mocked or faked where appropriate.
- **Testing distribution:** PhishShield follows a cost-aware testing pyramid aligned with its hexagonal architecture. The target distribution is a health signal, not a hard quota:
  - `Domain`: 55-60%
  - `Application`: 20-25%
  - `Infrastructure/API`: 10-15%
  - `E2E/smoke`: 5-10%
- **Testing rationale:** pure `Domain` tests should carry most behavioral combinations because they are the cheapest, fastest, and most deterministic. `Application` tests validate orchestration and contracts. `Infrastructure` and API tests validate adapters and framework boundaries. `E2E` and smoke tests remain intentionally small because they are slower, more fragile, and more expensive to diagnose.
- **GitHub Actions:** the current CI pipeline runs backend tests, frontend tests and build, and a backend Docker health smoke workflow. Formatting, linting, and image publishing remain future improvements.
- **Community management:** public GitHub Issues are used for roadmap tracking with labels such as `enhancement` and `good first issue`, and Git tags are used for formal versioning such as `v1.0.0` and `v1.1.0`.
