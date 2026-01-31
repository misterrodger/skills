---
name: test-code-quality
description: Testing philosophy and code quality for test suites. Use when writing, reviewing, or refactoring tests in any codebase.
---

# Test Code Quality

## Philosophy

Tests are executable spec and documentation for future devs. Clarity beats DRY. Test at the right level.

## Code Style

- Follow lightweight FP-inspired paradigm from general coding practices
- **DRY is negotiable** — repeat yourself if it aids understanding
- A dev a year from now should see context without jumping between many files/helpers

## Test Structure

- **AAA** — Arrange-Act-Assert. Visually separate them. Scannable at a glance.
- **One behavior per test** — multiple `expect` calls fine if same behavior. Don't test unrelated things together.
- **Parameterise** when similar tests multiply — but keep params readable

## Test Naming

Name tests as behavior: `rejectsExpiredTokens`, not `testToken`. What broke should be obvious from the name.

## Test Data

- Realistic, not `foo`/`bar`. Inline what matters, factory the rest.
- Colocate with shared types/schemas. Auto-generate from schemas where possible. Let types validate your fixtures.

## Test Isolation

Test files run in any order, concurrently. Seed DB per file. No cross-file state leakage.

## Failure Handling

- **Fail loud** — message should diagnose without re-running in debug
- **Quiet expected failures** — mock expected error logging to reduce noise. Keep mocks easy to comment out for debugging.

## What to Unit Test

Unit test when it helps validate correctness or aids future maintainability:
- Business logic
- Data transformations
- Code with multiple execution paths
- Pure functions with meaningful logic

## When to Skip Unit Tests

If a unit test adds little value:
- **Raise up** — cover it in an integration test as part of a larger execution path
- Don't test trivial getters, simple pass-throughs, or framework glue

## Generally Don't Test Internals

Test observable behavior, not implementation details. Exception: internal tests that aid developing or maintaining complex business logic.

## Test Levels

| Level | When to use |
|-------|-------------|
| Unit | Isolated logic, transforms, multiple paths |
| Integration | Multiple units working together, API boundaries |
| E2E | Happy-path acceptance, user flows |

Push testing to the lowest level that gives confidence. Raise up when unit tests would just duplicate integration coverage.