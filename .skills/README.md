# PhishShield Skills

This folder contains project-specific skills for **PhishShield**.

The official Anthropic `skill-creator` skill is installed in this project through the `skills` CLI and is available at:

```text
.agents/skills/skill-creator/
```

Official command used:

```bash
npx skills add anthropics/skills --skill skill-creator --yes
```

`skill-creator` must be used to create, improve, evaluate, and maintain repository-specific skills.

## Mandatory rule for creating skills

Every new PhishShield skill must be created using the official skill as the model:

```text
.agents/skills/skill-creator/
```

Minimum required workflow:

1. capture the skill intent,
2. define when the skill should trigger,
3. write `SKILL.md` with `name` and `description` frontmatter,
4. keep the skill actionable, specific, and aligned with PhishShield,
5. create initial evals when the skill is objectively testable,
6. verify alignment with `AGENT.md` and `doc/ADR.md`,
7. update this index.

Do not create skills without following this process.

## Language policy

All project skills, evals, prompts, assertions, examples, and documentation must be written in English.

Do not add Spanish text to skills or repository files. The only acceptable exceptions are explicit multilingual fixtures or samples where language itself is the behavior under test.

## Mandatory references

Every PhishShield skill must respect:

- `AGENT.md`
- `doc/ADR.md`

If a skill conflicts with the ADR, the ADR takes precedence.

## Conventions

Each project skill must live in its own folder:

```text
.skills/
  skill-name/
    SKILL.md
```

Each `SKILL.md` must include:

- frontmatter with `name` and `description`,
- skill purpose,
- when to use the skill,
- specific instructions for the agent,
- relevant internal references,
- quality criteria or a checklist.

## Planned skills

Initial folders are prepared, and skills are defined progressively with `skill-creator`.

- `phishshield-architecture`  
  Guides architectural changes, layer separation, port/adapter decisions, and alignment with `doc/ADR.md`.  
  Status: defined in `.skills/phishshield-architecture/SKILL.md` with initial evals in `.skills/phishshield-architecture/evals/evals.json`.

- `phishshield-backend`  
  Guides Python, FastAPI, use cases, contracts, validation, and backend adapters.  
  Status: defined in `.skills/phishshield-backend/SKILL.md` with initial evals in `.skills/phishshield-backend/evals/evals.json`.

- `phishshield-frontend`  
  Guides React, TypeScript, Vite, and forensic dashboard UI work.

- `phishshield-security-analysis`  
  Guides phishing analysis modules: headers, links, homoglyphs, attachments, OCR, EXIF, YARA, and sandboxing.

- `phishshield-testing`  
  Guides unit testing, integration testing, mocks, Pytest, TDD Red-Green-Refactor, and forensic module validation.  
  Status: defined in `.skills/phishshield-testing/SKILL.md` with initial evals in `.skills/phishshield-testing/evals/evals.json`.

## Created skills

Skills created with this workflow:

- `phishshield-backend`
- `phishshield-architecture`
- `phishshield-testing`