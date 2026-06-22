---
name: phishshield-testing
description: Specialized guidance for testing and TDD in PhishShield. Use this skill whenever the user asks to create, modify, or review tests, apply TDD, design Pytest cases, test pure domain functions, validate use cases, mock ports, test adapters, review coverage, or implement a new function with a Red-Green-Refactor workflow. Also use it when the user asks to implement new logic, even if tests are not explicitly mentioned, because PhishShield development should start with tests whenever behavior is verifiable.
---

# phishshield-testing

## Purpose

Guide AI agents to develop PhishShield with a clear, incremental testing discipline compatible with hexagonal architecture.

This skill exists to avoid implementing logic first and adding superficial tests later. It is especially important before implementing the first pure `domain` functions.

The default cycle is:

```text
Red -> Green -> Refactor
```

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

1. Define the expected behavior clearly.
2. Write the smallest failing test.
3. Run the test or state the exact command that should be run.
4. Confirm the **Red** state.
5. Implement the minimum code required to pass.
6. Run the affected test.
7. Confirm the **Green** state.
8. Refactor only if it improves clarity without changing behavior.
9. Run the affected tests again.
10. Repeat with the next case.

Do not group too many cases into one iteration. Keep changes small.

## Expected response shape

When using this skill, structure the answer as follows when applicable:

```text
1. Behaviour under test
2. Test scope
3. Red test to add
4. Minimal implementation needed for Green
5. Refactor considerations
6. Test command
7. Next test case
```

If code should not be implemented yet, provide only the test plan.

## TDD patterns

### Red-Green-Refactor

Use this cycle by default.

```text
Red: the test fails because the behavior does not exist.
Green: the minimum implementation passes the test.
Refactor: cleanup without changing behavior.
```

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
- use fakes or mocks for ports;
- verify orchestration;
- avoid real adapters;
- cover application errors;
- cover optional flows such as disabled AI.

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
- [ ] The minimum implementation does not break hexagonal architecture.

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