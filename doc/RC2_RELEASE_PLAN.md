# v0.1.0-rc.2 Release Plan

## Purpose

This document defines the remaining work to prepare PhishShield as a public,
local-first MVP for community evaluation.

The goal is not to complete every capability in the long-term architecture. The
goal is to publish a useful and understandable deterministic email-triage tool,
while preserving a clear path for future improvements driven by real usage.

## Product Position

PhishShield is a local, explainable phishing-email triage workbench for `.eml`
files.

Primary audience:

- IT analysts;
- security analysts;
- small security teams;
- technically capable homelab users.

Primary workflow:

```text
upload .eml
    -> inspect sender, URLs, attachments, authentication and findings
    -> understand deterministic risk posture
    -> export evidence or share the result
```

The Web UI is the primary product experience. The API, CLI and CI artifact
workflow are complementary integrations.

The product must not claim to be a universal phishing detector, malware verdict,
replacement for organizational email security controls, or replacement for
human incident-response judgment.

## Decisions

The following decisions are approved for RC.2:

```text
License:
  MIT
  Copyright (c) 2026 PhishShield contributors

Deployment:
  Docker Compose complete deployment

Startup command:
  docker compose up --build

Default UI:
  http://localhost:8080

Network exposure:
  frontend exposed to the host
  backend internal-only by default

Release:
  v0.1.0-rc.2

Container registry:
  GitHub Container Registry (GHCR)

Community:
  GitHub Discussions for ideas and use cases
  maintainers retain final priority and delivery decisions

Real email collection:
  not provided through GitHub Issues or Discussions

Public repository:
  curated clone of the private development repository
```

## Scope Of RC.2

### Included

- deterministic `.eml` analysis;
- MIME, plain-text and HTML extraction;
- sender and domain analysis;
- URL analysis;
- attachment filename and metadata analysis;
- SPF, DKIM and DMARC result analysis when present;
- social-engineering indicators;
- explainable findings with category and severity;
- deterministic risk score;
- Web UI analyst workbench;
- FastAPI endpoint;
- Markdown, JSON and HTML exports;
- deterministic single-email CLI;
- reusable GitHub Actions artifact workflow;
- CI guardrails phase one;
- complete local Docker Compose deployment;
- MIT open-source release hygiene;
- user-facing documentation index;
- deployment, contribution, security and public roadmap documentation.

### Experimental but Included Transparently

The optional advisory model branch remains available as experimental tooling:

- disabled by default;
- local artifact only;
- scope-aware;
- abstention-aware;
- separate from deterministic findings and `risk_score`;
- not a CI gate;
- not product-ready;
- not a universal phishing classifier.

### Deferred

- production-grade ML promotion;
- family-specific model training with authorized data;
- batch CLI analysis;
- JSONL batch output;
- SARIF output;
- OCR;
- YARA scanning;
- PDF and Office parsing beyond current metadata scope;
- macro analysis;
- browser or sandbox evidence capture;
- short-link resolution;
- attachment hash intelligence lookups;
- persisted analysis history;
- user accounts and multi-user operation;
- cloud dependency in the main analysis path;
- hosted production platform;

Deferred items remain possible future work. They are not promises or RC.2
acceptance criteria.

## Execution Phases

### Phase 1: Release Cleanup

Separate product distribution from local AI tooling and development state.

Tasks:

- remove tracked `.agents/` from the public distribution;
- remove `skills-lock.json` from the public distribution;
- add `.agents/` to `.gitignore`;
- keep `AGENT.md` as concise project and contribution guidance;
- keep `.skills/` as optional project-specific playbooks;
- ensure `.agents/` and `skills-lock.json` are not required to run the product;
- audit repository content for personal paths, personal usernames, secrets,
  datasets, model artifacts, evaluation outputs and local tool state;
- keep external data references portable with `<PHISHSHIELD_DATA_ROOT>`.

Expected outcome:

```text
The repository can be cloned and used without local AI tooling.
```

### Phase 2: Documentation Entry Point

Create the parent documentation page:

```text
doc/index.md
```

The index should guide a new visitor by purpose rather than by implementation
history.

Recommended structure:

```text
Start here
  -> What PhishShield does
  -> What it does not do
  -> Quick start with Docker Compose
  -> Analyze an .eml in the Web UI
  -> Understand findings and risk
  -> Export results

Automation and integrations
  -> CLI
  -> API
  -> GitHub Actions artifact workflow

Operate and deploy
  -> Deployment guide
  -> Runtime configuration
  -> Privacy and safety limits

Contribute and understand
  -> Contributing
  -> Security policy
  -> Architecture and ADR
  -> Roadmap
  -> Changelog

Research and experimental work
  -> Experimental advisory inference
  -> ML documentation
```

Update `README.md` into a visual product landing page:

- product statement;
- analyst-focused workflow;
- quick Docker Compose start;
- Web UI as the primary experience;
- CLI, API and CI as complementary integrations;
- deterministic findings and exports;
- privacy and safety limits;
- prominent link to `doc/index.md`.

Do not include TFM-specific language in public product documentation.

### Phase 3: Open-Source Hygiene

Add:

```text
LICENSE
CONTRIBUTING.md
SECURITY.md
doc/ROADMAP.md
```

`LICENSE`:

```text
MIT
Copyright (c) 2026 PhishShield contributors
```

`CONTRIBUTING.md` should cover:

- development installation;
- backend, frontend, CLI and test commands;
- hexagonal architecture rules;
- fixture and scoring policy;
- no real emails, datasets, models, secrets or sensitive results in Git;
- GitHub Discussions for ideas;
- Issues for accepted and reproducible work.

`SECURITY.md` should cover:

- responsible vulnerability reporting;
- not posting credentials, sensitive emails, active malicious files or
  confidential data publicly;
- product scope and security limitations.

`doc/ROADMAP.md` should be short and public-facing:

```text
Available now
  -> deterministic .eml triage
  -> Web UI, API, CLI and exports
  -> local Docker Compose deployment
  -> CI artifact analysis workflow
  -> optional experimental advisory inference

Planned directions
  -> batch CLI
  -> JSONL automation
  -> SARIF integration
  -> parser improvements driven by evidence
  -> reporting and workflow improvements
  -> optional local history if justified

Explicitly deferred
  -> OCR, YARA, PDF/Office/macros and browser evidence
  -> production-grade ML promotion
  -> cloud hosting, accounts and multi-user operation
```

The roadmap must state:

```text
Community feedback is welcome. Maintainers retain final ownership of
prioritization, scope and delivery. Roadmap items are not delivery commitments.
```

### Phase 4: Complete Docker Compose MVP

The target user experience is exactly one command:

```bash
docker compose up --build
```

Then the user opens:

```text
http://localhost:8080
```

Runtime architecture:

```text
Browser
  -> frontend production container :8080
  -> /api reverse proxy
  -> backend container :8000 on an internal Compose network
```

Requirements:

- production frontend image;
- frontend serves the built Vite application;
- frontend proxies `/api` to the backend service;
- only frontend is published to the host by default;
- backend remains internal-only in the product Compose profile;
- no database;
- no users or authentication;
- no persistence or history;
- no cloud dependency;
- advisory model disabled by default;
- runtime configuration documented through `.env.example`;
- upload size limit remains configurable;
- privacy warning is visible in documentation and UI;
- create `doc/DEPLOYMENT.md`.

`doc/DEPLOYMENT.md` should document:

- prerequisites: Docker and Compose;
- one-command startup;
- URL and port configuration;
- logs;
- stopping and cleaning containers;
- upload-size configuration;
- local-network exposure warnings;
- data retention behavior;
- optional native development path separately from product deployment.

### Phase 5: Fresh Deployment Validation

Validate from a clean environment:

```text
docker compose up --build
  -> frontend reachable at localhost:8080
  -> Web UI upload works
  -> benign fixture produces LOW
  -> suspicious fixture produces CRITICAL
  -> Markdown export works
  -> JSON export works
  -> HTML export works
  -> upload limit is enforced
  -> backend is not exposed by default
  -> advisory model remains disabled
```

The complete Compose smoke test is now part of CI alongside the existing backend
Docker smoke.

### Phase 6: Community Readiness

Enable one GitHub Discussions category:

```text
Ideas and Use Cases
```

Use it for:

- workflows users need;
- integration ideas;
- deployment questions;
- practical feedback.

Do not add:

- a real-email submission channel;
- a public sample collection process;
- a formal voting system;
- a promise to implement every suggestion;
- a large project-management system before demand exists.

Do not request or accept real corporate emails through public GitHub channels.

### Phase 7: Public Repository Export

The current private repository remains intact as the complete development
archive. A separate public clone is created from the RC.2 state.

The public export process should:

- preserve the full commit graph and commit order;
- normalize author and committer identity;
- normalize timestamps for privacy while preserving topological order;
- sanitize personal paths, usernames, private branch references and sensitive
  historical content;
- remove local AI tooling that is not part of distribution;
- recreate public tags;
- run content, secret, license and test audits;
- publish only after the exported clone passes review.

This is a manual release operation, not a daily automatic synchronization. The
public repository becomes the community-facing release and contribution channel
after publication.

The public repository should include a transparent note that historical commit
metadata was normalized for privacy while project order and release traceability
were preserved.

### Phase 8: GHCR And Public Demo

After Compose and RC.2 validation:

- publish versioned frontend and backend images to GHCR;
- use explicit tags such as `v0.1.0-rc.2`;
- do not publish `latest` while the project is an RC;
- use Git tags as the relationship between source and images;
- deploy a public demo only when HTTPS, retention, access and upload controls
  are understood.

The public demo should be deterministic-only:

- advisory model disabled;
- no persistence;
- no email history;
- no external link resolution;
- no browser rendering;
- no attachment execution;
- no public backend port;
- clear warning not to upload confidential or production email;
- short operational log retention;
- rate limiting at the reverse proxy where appropriate.

### Phase 9: RC.2 Preparation

Update:

```text
CHANGELOG.md
README.md
doc/DEPLOYMENT.md
doc/ROADMAP.md
doc/POST_MVP_ROADMAP.md
doc/ENGINEERING_JOURNEY.md
```

RC.2 should describe:

```text
Included
  deterministic Web UI, API, CLI and exports
  artifact CI workflow
  CI guardrails phase one
  full local Compose deployment
  onboarding, deployment, contribution and security documentation

Experimental
  optional scope-aware advisory inference
  disabled by default
  never changes deterministic findings or risk score

Deferred
  production ML promotion
  batch and SARIF
  OCR, YARA, PDF/Office and browser capabilities
  persistence, accounts and cloud platform
```

Only after validation should the project propose the public tag:

```text
v0.1.0-rc.2
```

The tag and public repository are not created automatically by development
tasks.

## Acceptance Criteria

The RC.2 MVP is ready for community evaluation when a new user can do this
without understanding the repository internals:

```bash
git clone <repository>
cd PhishShield
```

Then:

```text
open http://localhost:8080
upload an .eml
understand the deterministic result
export evidence
find the correct documentation path
```

The release is not blocked on:

- production-grade ML;
- OCR, YARA, browser, PDF or Office capabilities;
- batch or SARIF;
- persistence or hosted multi-user operation;
- community feedback before publication.

Community feedback begins after the MVP is understandable and usable.

## After RC.2

The project remains open to future work without becoming an endless commitment.
Future requests are evaluated against:

1. What current workflow is not served?
2. Who needs the capability and how often?
3. Can it be delivered without opening an unnecessary platform?
4. What security, privacy and maintenance cost does it add?
5. Is there evidence beyond a single speculative request?

Possible future directions include:

- batch CLI if users need folder analysis;
- SARIF if a concrete security-platform integration appears;
- parser maintenance driven by real reproducible samples;
- scoring calibration driven by a concrete false-positive or false-negative
  question;
- authorized family-level data for future advisory model training;
- forensic extensions only when a dedicated workflow justifies them.

The maintainers decide which suggestions become implementation work.
