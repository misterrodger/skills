---
name: dev-coding-practices
description: Functional-first coding style and workflow. ALWAYS apply when writing, editing, or generating ANY code — application code, tests, scripts, data pipelines, utilities, or any other code artifacts. Invoke this before producing any code output.
---

# Developer Coding Practices

## Philosophy

Functional-lite. Fail fast. Defer defense. Ship the meaningful change, abstract the rest.

## Functional Style

- **Declarative over imperative** — say what, not how
- **Immutable by default** — mutate only for perf (1000s of objects)
- **Pure functions** — separate data from functions that operate on it
- **Segregate state** — isolate side-effects, avoid shared state
- **Composition over inheritance** — curry, compose, pipe
- **Unary functions** — general config first, specific data last
- **Point-free when clean** — reduce temp variables, reduce surface area
- **Recursion over loops** — but mind the tail-call stack

## Code Style

- Descriptive names, readable syntax — no abbreviations unless universal
- Variables: follow language convention (camelCase JS/TS, snake_case Python)
- Files/folders: kebab-case
- No comments or explanations in code
- No defensive coding in first iterations
- Fix data issues upstream, not with defensive checks
- Defer validation, error handling, logging, metrics until asked
- Mention critical edge cases in chat; don't code them unsolicited

## JS/TS Specifics

- `undefined` only, never `null`

## Architecture

**Orchestrator → Pipeline → Helpers**

1. Main function: receives inputs, coordinates
2. Data pipeline: transforms through helper chain
3. Helpers: one logical chunk each, easily testable

Main can be long. Helpers stay focused. No arbitrary length rules.

## Organization

- Helpers live with orchestrator until 2-3+ accumulate
- Extract testable logic: transforms, algorithms, pure business logic
- Isolate side-effects

## App vs Library Code

| Concern | App Code | Library Code |
|---------|----------|--------------|
| Optimize for | Readability, dev speed | Performance |
| Typing | Inference | Explicit |
| Mutability | Immutable | Perf-justified |

## Config

- Constants → constants file
- Config → config file
- Validate config before runtime

## Problem-Solving

1. Decompose: iterator, transform, state
2. Patterns repeated 2-3x → make generic
3. Custom parts reveal themselves
4. 10x = show the change, hide the noise