# PhishShield Documentation

This is the documentation map for PhishShield. Start with the path that matches
what you want to do.

## Start Here

- [Project README](../README.md): product overview and quick start.
- [RC.2 release plan](RC2_RELEASE_PLAN.md): scope and acceptance criteria for the current MVP release candidate.
- [Changelog](../CHANGELOG.md): notable released and unreleased changes.

## Use PhishShield

### Analyst

The primary workflow is the Web UI:

```text
upload .eml
  -> inspect extracted evidence
  -> review findings and risk
  -> export a report
```

The Web UI is designed to help an analyst inspect sender identity, URLs,
attachments, authentication results, and social-engineering indicators without
opening the suspicious message in a normal mail client.

The complete one-command Docker Compose deployment is being prepared for
`v0.1.0-rc.2`.

### Operator

- [Deployment guide](DEPLOYMENT.md): local Compose deployment, runtime operations, and GHCR images.
- [Runtime configuration](API.md#configuration): upload limits and optional advisory settings.
- [Security policy](../SECURITY.md): responsible disclosure and safe use.

### Integrator

- [API contract](API.md): deterministic HTTP endpoint and response shape.
- [CLI guide](CLI.md): single-email analysis, JSON output, and stable exit codes.
- [GitHub Actions artifact workflow](CLI.md#github-actions-artifact-workflow): deterministic CI analysis.

### Contributor

- [Contributing guide](../CONTRIBUTING.md): development setup, tests, and contribution rules.
- [Architectural Decision Record](ADR.md): architectural source of truth.
- [Backend evolution plan](BACKEND_EVOLUTION_PLAN.md): backend boundaries and current direction.
- [Frontend MVP plan](FRONTEND_MVP_PLAN.md): analyst workbench scope.
- [Engineering journey](ENGINEERING_JOURNEY.md): curated engineering milestones.

## Understand The Product

- [Public roadmap](ROADMAP.md): current capabilities and planned directions.
- [Post-MVP roadmap](POST_MVP_ROADMAP.md): detailed implementation tracks.
- [Scoring calibration](SCORING_CALIBRATION.md): deterministic risk-scoring evidence and change rules.
- [API contract](API.md): request, response, and error behavior.

## Experimental Advisory Inference

The advisory model is not required for the main product workflow.

- [Experimental advisory inference closure](EXPERIMENTAL_ADVISORY_INFERENCE.md): current status, scope gate, abstention, and limits.
- [Model-assisted analysis plan](MODEL_ASSISTED_ANALYSIS_PLAN.md): architecture and future direction.
- [ML training and evaluation strategy](ML_TRAINING_EVALUATION_STRATEGY.md): dataset roles and evaluation rules.
- [ML dataset research](ML_DATASET_RESEARCH.md): reviewed sources and evidence classification.
- [ML data preparation plan](ML_DATA_PREPARATION_PLAN.md): external preparation workflows.
- [Scope gate validation](ML_SCOPE_GATE_VALIDATION.md): scope-aware diagnostic results.

The advisory model remains optional, disabled by default, and separate from
deterministic findings and `risk_score`.

## Product Boundaries

PhishShield currently provides deterministic email triage. It does not claim to
be a universal phishing or malware verdict. The following remain deliberately
deferred until a concrete workflow justifies them:

- OCR;
- YARA scanning;
- PDF and Office parsing beyond current metadata scope;
- macro analysis;
- browser or sandbox evidence capture;
- short-link resolution;
- attachment reputation lookups;
- batch CLI and SARIF;
- persistence, accounts, and multi-user operation;
- cloud hosting as a required dependency;
- production-grade advisory model promotion.

## Community Feedback

GitHub Discussions are available for ideas, use cases, and deployment feedback.
Please describe the workflow and problem rather than only requesting a feature.
Maintainers decide which suggestions become implementation work.

Do not post real corporate email, credentials, confidential content, active
malicious attachments, or sensitive datasets in public GitHub channels.
