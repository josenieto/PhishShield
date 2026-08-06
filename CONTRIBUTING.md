# Contributing To PhishShield

Thank you for helping improve PhishShield. Contributions should improve a
demonstrated email-triage workflow while preserving the local-first,
deterministic core.

## Before Starting

- Read [`docs/index.md`](docs/index.md) for project navigation.
- Read [`docs/ADR.md`](docs/ADR.md) before architecture or contract changes.
- Check [`docs/POST_MVP_ROADMAP.md`](docs/POST_MVP_ROADMAP.md) and
  [`docs/ROADMAP.md`](docs/ROADMAP.md) for current direction.
- Open a GitHub Discussion for broad ideas and use cases before proposing a
  large implementation.

## Development Setup

```bash
python -m pip install -e ".[test,dev]"
python -m pre_commit install
python -m pre_commit install --hook-type commit-msg
```

Optional ML experiments require:

```bash
python -m pip install -e ".[test,dev,ml]"
```

## Verification

Backend tests:

```bash
python -m pytest
```

Frontend tests and build:

```bash
cd frontend
npm ci
npm run test
npm run build
```

All local guardrails:

```bash
python -m pre_commit run --all-files
```

The deterministic CLI is tested with:

```bash
phishshield analyze tests/fixtures/emails/suspicious_html_notice.eml --format json --fail-on high
```

## Architecture Rules

PhishShield follows:

```text
Domain <- Application <- Infrastructure / Entrypoints
```

- Keep Domain rules pure and deterministic.
- Keep external formats, frameworks, filesystem, and runtime details in Infrastructure.
- Coordinate behavior through Application use cases and ports.
- Do not duplicate parser, finding, scoring, or risk logic in CLI or API entrypoints.
- Keep advisory model assessment optional and separate from deterministic results.

## Fixtures And Scoring

- Add a realistic fixture for behavior changes.
- Update `docs/SCORING_CALIBRATION.md` for scoring-sensitive changes.
- Do not change weights or critical indicators without evidence.
- Keep tests and fixture content in English unless multilingual behavior is under test.

## Data And Secrets

Do not commit:

- real or confidential email;
- personal data;
- credentials, tokens, or private keys;
- active malicious attachments or dangerous URLs;
- downloaded datasets or prepared JSONL;
- model artifacts or detailed evaluation outputs;
- local AI-tool installations.

Keep research data outside the repository under a local path such as
`<PHISHSHIELD_DATA_ROOT>`.

## Pull Requests

Pull requests should explain:

- the user or engineering problem;
- the smallest useful change;
- affected contracts or layers;
- tests and verification performed;
- security and privacy considerations;
- deferred follow-up, if applicable.

Maintainers retain final ownership of priority, scope, and release decisions.
