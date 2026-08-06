---
name: phishshield-security-analysis
description: Guidance for PhishShield forensic indicator analysis. Use this skill when creating, reviewing, or extending phishing detection rules, pure Domain analysis helpers, URL/domain/text/attachment/authentication/risk indicators, finding codes, or Application use cases that compose security indicators. It helps decide which forensic logic can remain pure, which behavior requires Application orchestration, and how to avoid network, DNS, filesystem, parsers, OCR, YARA, AI, browser access, or other infrastructure in Domain.
---

# phishshield-security-analysis

## Purpose

Guide PhishShield forensic indicator work in `Domain` and `Application` without drifting into infrastructure.

PhishShield detects phishing indicators from emails, links, domains, attachments, authentication results, visible text, and future analysis modules. Many useful indicators can be implemented as deterministic pure rules, but some capabilities require use cases, ports, adapters, or external tools. This skill helps agents draw that line consistently.

This skill does not implement concrete FastAPI endpoints, HTTP clients, OCR, YARA, Playwright, Ollama, or parsers. Use backend or architecture skills for those boundaries.

## References to consult

Before designing or reviewing forensic analysis logic, read:

- `AGENT.md`
- `doc/ADR.md`
- `doc/DOMAIN_PURE_FUNCTIONS_PLAN.md`
- `.skills/README.md`

If this skill conflicts with `doc/ADR.md`, the ADR takes precedence.

## When to use this skill

Use this skill when the task involves:

- phishing indicators;
- pure `Domain` analysis helpers;
- finding codes or indicator names;
- domain analysis;
- URL analysis;
- suspicious Unicode or homoglyph signals;
- text normalization and social engineering heuristics;
- attachment metadata or filename rules;
- authentication result interpretation;
- risk scoring;
- finding composition;
- deciding whether completed pure helpers justify an `Application` use case.

Do not use this skill as the primary guide for:

- FastAPI endpoint implementation;
- concrete adapters;
- HTTP requests;
- DNS queries;
- browser sandboxing;
- OCR execution;
- YARA execution;
- parsing real `.eml`, PDF, Office, or image files;
- Docker or deployment work.

Use `phishshield-architecture` first if the main question is layer placement or port/adapter design. Use `phishshield-testing` for the TDD workflow.

## Working process

When this skill triggers:

1. Identify the indicator type and the input artifact.
2. Decide whether the behavior can be pure `Domain` logic.
3. Define the function or use case contract before implementation.
4. List normal cases, edge cases, and hostile-input cases.
5. Use `phishshield-testing` for Red-Green-Refactor-Verify when behavior is verifiable.
6. Keep deterministic indicator rules in `Domain` when they need no IO or external tool.
7. Move to `Application` only when composing meaningful behavior or exposing a system action.
8. Require ports/adapters only when crossing an infrastructure boundary.
9. Preserve evidence that explains why a finding was produced.

## Domain-safe indicator rules

A rule can usually live in `Domain` when it:

- receives primitive values or domain models;
- returns primitive values or domain models;
- is deterministic;
- has no side effects;
- performs no network, DNS, filesystem, browser, AI, OCR, YARA, parser, or external SDK work;
- can be tested with simple Pytest unit tests.

Good `Domain` examples:

```python
contains_punycode(domain: str) -> bool
has_suspicious_tld(domain: str, suspicious_tlds: set[str]) -> bool
has_embedded_credentials(url: str) -> bool
has_suspicious_query_density(url: str, threshold: int) -> bool
has_url_shortener_domain(domain: str, known_shorteners: set[str]) -> bool
classify_authentication_risk(spf_result: str, dkim_result: str, dmarc_result: str) -> str
has_double_extension(filename: str) -> bool
```

## Application composition rules

Create an `Application` use case when there is meaningful orchestration across multiple domain rules or when the system needs a coherent analysis result.

Good `Application` examples:

```text
AnalyzeDomainIndicatorsUseCase
AnalyzeUrlIndicatorsUseCase
AnalyzeAttachmentIndicatorsUseCase
```

A use case should:

- receive a command object;
- coordinate pure domain helpers;
- return an explicit analysis result;
- preserve useful evidence;
- expose finding codes in a stable order when order matters;
- remain free from concrete adapters and frameworks.

Do not create an `Application` use case just because one helper exists. Move upward when the use case composes meaningful behavior.

## What must not live in Domain

Keep these outside `Domain`:

- resolving short URLs through `HEAD` or `GET` requests;
- following redirects;
- querying DNS;
- opening a browser or taking screenshots;
- parsing real `.eml`, PDF, Office, or image files with external libraries;
- running OCR;
- running YARA;
- calculating hashes from files on disk;
- calling Ollama or any AI SDK;
- reading environment variables or mutable global configuration;
- using FastAPI, Pydantic API schemas, or framework request objects as domain entities.

Use `Application` ports and `Infrastructure` adapters when any of these capabilities are required.

## Finding codes and evidence

Finding codes should be stable, explicit, and useful for later reporting.

Recommended style:

```text
DOMAIN_CONTAINS_PUNYCODE
DOMAIN_HAS_SUSPICIOUS_TLD
URL_HAS_EMBEDDED_CREDENTIALS
URL_HAS_SUSPICIOUS_QUERY_DENSITY
URL_USES_KNOWN_SHORTENER_DOMAIN
```

When possible, return supporting evidence alongside booleans:

- labels;
- scripts;
- confusable characters;
- matched TLD;
- query parameter count;
- matched shortener domain;
- original input.

Preserve original input when it has forensic value. Normalize derived fields for comparison, not necessarily the stored input.

## Relationship with other skills

- Use `phishshield-testing` for Red-Green-Refactor-Verify implementation workflow.
- Use `phishshield-architecture` for layer checkpoints, port/adapter decisions, or ADR conflicts.
- Use `phishshield-backend` when implementing use cases, ports, adapters, FastAPI, parsers, or backend integration details.
- Use a compatible skill-authoring workflow to create, evaluate, or modify project skills.

If a recurring specialist area appears and no suitable skill exists, pause feature development and create or improve the skill using the documented project skill workflow instead of repeatedly relying on ad hoc guidance.

## Rejection criteria

Reject or redesign a forensic-analysis proposal if it:

- adds network, DNS, filesystem, browser, AI, OCR, YARA, parser, or external SDK access to `Domain`;
- hides infrastructure behind a pure-looking helper;
- creates a port for a deterministic pure function;
- creates an `Application` use case for a single isolated helper without meaningful composition;
- emits vague findings that cannot be traced to evidence;
- treats AI or external reputation as the only source of truth;
- ignores hostile or malformed inputs.

## Checklist before finishing forensic indicator work

- [ ] The affected layer is clear.
- [ ] Pure rules stay in `Domain`.
- [ ] Use cases compose meaningful behavior in `Application`.
- [ ] Infrastructure boundaries are not crossed without a port/adapter decision.
- [ ] Findings are stable and evidence-backed.
- [ ] Edge cases and hostile inputs are covered.
- [ ] Tests follow the expected PhishShield TDD workflow.
- [ ] The solution preserves the local/self-hosted privacy model.

## Suggested eval prompts

Use these prompts to check whether the skill guides the agent well:

1. `Add a pure helper to detect known URL shortener domains.`
2. `Decide whether resolving bit.ly redirects belongs in Domain.`
3. `Create a rule for suspicious attachment double extensions.`
4. `Interpret SPF, DKIM, and DMARC results already computed by infrastructure.`
5. `Design AnalyzeUrlIndicatorsUseCase after URL helpers are complete.`

A good answer should preserve Domain purity, identify when Application orchestration is justified, avoid infrastructure in pure rules, and keep findings evidence-backed.
