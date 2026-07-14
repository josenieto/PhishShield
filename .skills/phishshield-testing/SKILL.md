---
name: phishshield-testing
description: Specialized guidance for testing and TDD in PhishShield. Use this skill whenever the user asks to create, modify, or review tests, apply TDD, design Pytest cases, test pure domain functions, validate use cases, mock ports, test adapters, review coverage, refactor safely, or implement new behavior with a Red-Green-Refactor-Verify workflow. Also use it when the user asks to implement new logic, even if tests are not explicitly mentioned, because PhishShield development should start with tests whenever behavior is verifiable.
---

# phishshield-testing

## Purpose

Guide AI agents to develop PhishShield with a clear, incremental testing discipline compatible with hexagonal architecture.

This skill exists to avoid implementing logic first and adding superficial tests later. It is especially important before implementing the first pure `domain` functions.

The default cycle is:

```text
Red -> Green -> Refactor -> Verify
```

PhishShield also uses a cost-aware testing distribution guideline. Treat it as a health signal, not a hard quota:

- `Domain`: 55-60%
- `Application`: 20-25%
- `Infrastructure/API`: 10-15%
- `E2E/smoke`: 5-10%

The reason for this shape is practical:

- `Domain` tests are the cheapest, fastest, and most deterministic, so they should carry most behavior combinations.
- `Application` tests verify orchestration, ports, contracts, deduplication, and scoring flow.
- `Infrastructure` and API tests verify parser behavior, adapters, framework boundaries, configuration, and serialization.
- `E2E` and smoke tests are valuable but expensive, so they should stay focused on a few critical flows.

Do not add artificial tests to satisfy percentages. Use the distribution to detect imbalance or excessive reliance on slow tests.

Use classic TDD patterns when appropriate:

- Fake it till you make it
- Triangulation
- Obvious implementation
- Arrange / Act / Assert
- Given / When / Then
- Make it work, make it right, make it fast

## References to consult

Before designing relevant tests, read:

- `AGENT.md`
- `doc/ADR.md`
- `doc/DOMAIN_PURE_FUNCTIONS_PLAN.md`
- `.skills/README.md`

If the task affects architecture or layer boundaries, use `phishshield-architecture` first.

If the task affects backend implementation, combine this skill with `phishshield-backend`.

## When to use this skill

Use this skill when the task involves:

- creating tests;
- applying TDD;
- implementing a new function;
- modifying existing behavior;
- testing pure domain functions;
- designing Pytest tests;
- creating fixtures;
- reviewing fragile tests;
- testing Application use cases;
- mocking ports;
- testing Infrastructure adapters;
- validating errors, limits, or hostile inputs;
- refactoring safely;
- adding coverage to forensic modules.

Also use it when the user says something like:

```text
let's implement this function
```

because the expected workflow in this project is to start with expected behavior and tests.

## Mandatory TDD process

When behavior is verifiable, work as follows:

1. Check repository status before editing.
2. Define the expected behavior clearly.
3. Write the smallest failing test.
4. Run the test or state the exact command that should be run.
5. Confirm the **Red** state and the expected failure reason.
6. Implement the minimum code required to pass.
7. Run the affected test.
8. Confirm the **Green** state.
9. Review the **Refactor** step explicitly.
10. Refactor only if it improves clarity without changing behavior.
11. If no cleanup is useful, state `Refactor not needed.`
12. Run affected tests again when refactoring changes code.
13. **Verify** with the affected test scope and the full suite when it is still cheap.
14. Stop before committing unless the user explicitly asks the agent to commit.
15. Repeat with the next case.

Do not group too many cases into one iteration. Keep changes small.

### Full-suite verification triggers

Run the full backend suite with:

```bash
python -m pytest
```

before marking work complete when a change touches any of these shared backend contracts:

- `domain/value_objects/*`;
- Domain finding definitions;
- Application result models or summaries;
- API response schemas;
- parser adapters that feed multiple layers;
- configuration defaults reused across tests and runtime wiring.

Run frontend verification with:

```bash
cd frontend
cmd /c npm run test
cmd /c npm run build
```

when a change touches:

- frontend API response types;
- shared UI result structures;
- analysis rendering components reused across the main flow.

Use partial test scopes during development, but do not treat them as final verification for cross-layer contract changes.

## Expected response shape

When using this skill, structure the answer as follows when applicable:

```text
1. Behaviour under test
2. Test scope
3. Red test to add
4. Minimal implementation needed for Green
5. Refactor considerations
6. Verification commands
7. Commit text or next test case
```

If code should not be implemented yet, provide only the test plan.

## TDD patterns

### Red-Green-Refactor

Use this cycle by default.

```text
Red: the test fails because the behavior does not exist.
Green: the minimum implementation passes the test.
Refactor: review cleanup without changing behavior.
Verify: run the affected scope and full suite when it is cheap.
```

The refactor phase is mandatory as a review step, but code changes are optional. If the implementation and tests are already clear, say `Refactor not needed.`

### Fake it till you make it

Useful for the first test of a function.

Example:

```python
def contains_invisible_chars(text: str) -> bool:
    return True
```

This is only acceptable as a temporary step for a very narrow first test. It must evolve as more tests are added.

### Triangulation

Add new cases to force generalization.

Example:

1. detects `\u200b`;
2. detects `\u200c`;
3. does not detect clean text;
4. handles empty string.

### Obvious implementation

If the solution is trivial and the risk is low, implement the clear version directly after writing tests.

### Arrange / Act / Assert

Recommended Pytest structure:

```python
def test_should_detect_zero_width_space():
    # Arrange
    text = "paypa\u200bl.com"

    # Act
    result = contains_invisible_chars(text)

    # Assert
    assert result is True
```

### Given / When / Then

Useful when behavior expresses a business rule:

```python
def test_given_clean_text_when_checking_invisible_chars_then_returns_false():
    text = "paypal.com"

    result = contains_invisible_chars(text)

    assert result is False
```

## Domain test rules

`domain` tests must be:

- unit-level;
- fast;
- deterministic;
- free from network access;
- free from filesystem access;
- free from FastAPI;
- free from Playwright;
- free from Ollama;
- free from YARA;
- free from OCR;
- free from external parsers;
- free from complex mocks.

If complex mocks are needed to test a domain function, that logic probably does not belong in the domain.

## Application test rules

`application` tests should:

- test use cases;
- use real pure Domain helpers by default;
- use fakes or mocks for ports;
- verify orchestration;
- avoid real adapters;
- cover application errors;
- cover optional flows such as disabled AI.

Do not mock pure Domain helpers just to isolate a use case. Application is allowed to depend on Domain, and using real Domain behavior gives confidence that orchestration and rules work together.

Use fakes or mocks for:

- Application ports;
- Infrastructure adapters;
- filesystem, network, browser, AI, OCR, YARA, external parsers;
- expensive, non-deterministic, or IO-bound collaborators.

Do not use fakes or mocks for:

- pure Domain helpers;
- deterministic value objects;
- pure scoring, finding, URL, domain, attachment, authentication, or social engineering rules.

If an Application test becomes slow because of a Domain helper, review whether the helper is still pure and belongs in Domain. Do not hide that problem with mocks.

Example:

```text
AnalyzeEmailUseCase -> mocked EmailParserPort + mocked LinkAnalyzerPort
```

## Infrastructure test rules

`infrastructure` tests may use fixtures and test doubles, but external effects must be controlled.

For adapters:

- mock network access;
- use controlled local fixtures;
- apply timeouts;
- avoid real services in unit tests;
- move real-service checks to explicit integration tests when necessary.

Examples:

- do not resolve real URLs in unit tests;
- do not open real Chromium in domain unit tests;
- do not call real Ollama in unit tests;
- do not depend on real Tesseract except in explicit integration tests.

## Cost-aware testing distribution

Use the following guidance when deciding where to add coverage:

- prefer `Domain` when the behavior is pure and deterministic;
- prefer `Application` when validating orchestration across real Domain helpers and mocked or faked ports;
- prefer `Infrastructure` when the risk lives in parsing, adapters, configuration, framework integration, or serialization;
- use `E2E` or smoke tests only for a few critical end-to-end user journeys.

When the suite starts to drift, use these questions:

1. Are we pushing too much behavior upward into expensive tests?
2. Are we missing cheap tests in `Domain` for core forensic rules?
3. Are API and adapter boundaries covered where parsing or configuration can break?
4. Are high-level tests duplicating lower-level coverage without adding confidence?

## Test timing and difficulty policy

Use lightweight quantitative checks to keep the feedback loop fast.

Timing guidance:

- The full unit-heavy suite should normally stay under 5 seconds at the current project stage.
- Any individual unit test above 250 ms should be reviewed.
- Pure Domain tests should normally be effectively instant and must not wait on IO.
- Application use case tests should stay fast and deterministic.
- Slower tests must be explicit integration tests or have a clear reason.

Use this command to inspect slow tests:

```bash
python -m pytest --durations=10
```

### Test difficulty levels

Use these levels to reason about test cost, isolation, and expected tooling.

```text
Level 1: Pure Domain function test.
```

- No mocks.
- No IO.
- No infrastructure.
- Fast and deterministic.

```text
Level 2: Application use case test with real Domain helpers.
```

- Tests orchestration.
- Uses real pure Domain helpers.
- Uses no concrete adapters.

```text
Level 3: Application use case test with fake or mock ports.
```

- Tests orchestration across boundaries.
- Uses fakes or mocks for ports.
- Uses no real Infrastructure.

```text
Level 4: Infrastructure adapter test with controlled fixtures.
```

- Tests concrete adapters.
- Uses mocks, local fixtures, or controlled resources.
- Covers timeouts and failures where relevant.

```text
Level 5: Integration or end-to-end test with real external components.
```

- Must be explicit.
- May be slower.
- Should not be part of the fast unit feedback loop unless intended.

### Mock and fake guidance

Mock or fake ports and external boundaries.

Do not mock pure Domain helpers by default. `Application` tests may use real Domain helpers because they are deterministic, fast, and dependency-free.

If a unit test needs many mocks, review the design boundary. It may indicate that infrastructure behavior leaked into an inner layer.

## Entrypoint / FastAPI test rules

API tests should:

- verify request validation;
- verify HTTP status codes;
- verify response serialization;
- mock use cases;
- avoid running full forensic analysis from the endpoint.

FastAPI should be tested as a system boundary, not as a place for business rules.

## Recommended naming

Use behavior-oriented test names.

Correct:

```python
def test_should_strip_zero_width_space_from_text():
    ...
```

```python
def test_should_return_false_when_text_has_no_invisible_chars():
    ...
```

Incorrect:

```python
def test_regex_works():
    ...
```

```python
def test_internal_loop():
    ...
```

## Suggested test organization

When the test structure is created, use:

```text
tests/
  unit/
    domain/
      services/
    application/
  integration/
    infrastructure/
    entrypoints/
  fixtures/
```

For the first pure domain function:

```text
tests/unit/domain/services/text_normalization/test_invisible_characters.py
```

For pure URL analysis helpers:

```text
tests/unit/domain/services/url_analysis/test_url_schemes.py
tests/unit/domain/services/url_analysis/test_embedded_credentials.py
tests/unit/domain/services/url_analysis/test_query_density.py
tests/unit/domain/services/url_analysis/test_shortener_domains.py
```

## Documentation scope

Do not document every small test edit. Update `doc/ENGINEERING_JOURNEY.md` when the test work represents a meaningful engineering step, such as a new function group, a completed group checkpoint, a new use case, a testing strategy change, or an important rejection decision.

For multiple small helpers inside the same function group, prefer concise grouped documentation unless a helper introduces a notable architectural or testing decision.

## Recommended first PhishShield case

Suggested first iteration:

```text
Text normalization - invisible characters
```

Functions:

```python
contains_invisible_chars(text: str) -> bool
strip_invisible_chars(text: str) -> str
```

Initial tests:

- detects zero-width space;
- detects zero-width non-joiner;
- detects zero-width joiner;
- returns false for clean text;
- strips invisible characters without changing visible text;
- handles empty string.

## Rejection criteria

Reject or redesign a testing approach if it:

- implements code before defining behavior;
- adds tests that depend on real network access without being explicit integration tests;
- tests internal details instead of behavior;
- uses Playwright/Ollama/YARA/OCR in domain unit tests;
- mixes domain tests with FastAPI;
- needs complex mocks for a pure function;
- misses basic edge cases;
- fails to verify errors or hostile input where relevant.

## Checklist before finishing a testing task

- [ ] The expected behavior is clear.
- [ ] At least one test fails before implementation when TDD applies.
- [ ] Tests are deterministic.
- [ ] Tests are in the correct layer.
- [ ] Tests do not depend on real infrastructure unless explicitly integration-level.
- [ ] Test names describe behavior.
- [ ] Normal and edge cases are covered.
- [ ] Affected tests were run or the exact command was provided.
- [ ] The refactor step was reviewed, even if no code changed.
- [ ] Full suite was run when it was cheap enough for the current stage.
- [ ] Slow tests were checked with `python -m pytest --durations=10` when timing is relevant.
- [ ] Test difficulty level is appropriate for the affected layer.
- [ ] Mocks or fakes are used for ports or infrastructure boundaries, not pure Domain helpers by default.
- [ ] The minimum implementation does not break hexagonal architecture.
- [ ] The agent stopped before commit unless explicitly asked to commit.

## Relationship with other skills

- Use `phishshield-architecture` first when there are doubts about layer, dependency, or boundary decisions.
- Use `phishshield-backend` together with this skill for endpoints, use cases, ports, or backend adapters.
- Use `phishshield-security-analysis` when it exists and the focus is a concrete forensic rule.
- Use this skill whenever behavior is verifiable.

## Suggested eval prompts

Use these prompts to check whether the skill guides the agent well:

1. `Create TDD tests for contains_invisible_chars before implementing the function.`
2. `Design unit tests for strip_invisible_chars following Red-Green-Refactor.`
3. `We want to test an adapter that resolves shortened URLs without using real network access.`
4. `Review these tests because they depend on Playwright in a domain function.`
5. `Add a new risk rule and design the Pytest tests first.`

A good answer should start from behavior, propose small tests, respect the correct layer, and avoid external dependencies in domain unit tests.
