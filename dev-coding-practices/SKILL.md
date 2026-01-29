---
name: dev-coding-practices
description: Coding style and workflow preferences for application and library code. Use when writing, reviewing, or refactoring code in any programming language for production applications or libraries. Applies to all code unless user specifies testing, functional programming, or other specialized contexts.
---

# Developer Coding Practices

## Core Philosophy

Write concise, functional-lite code that implements requirements directly and fails fast. Defer defensive patterns until explicitly needed.

## Code Style

- Prefer functional paradigm over OOP/class-based approaches
- Write concise implementations without code comments or explanations
- No defensive coding in first iterations - implement requirements and fail fast
- Resolve data issues upstream at the source, not through defensive checks
- Defer validation, error handling, logging, and metrics until requested
- Add these concerns minimally and only as needed

## Language-Specific Rules

### ECMA Languages (JavaScript/TypeScript)

- Avoid `null`, only use `undefined`

## Data & Mutability

- Prefer immutability by default
- Use mutable approaches only when performance issues are likely (thousands of objects or more)
- Performance concerns typically relevant in: library code, data processing pipelines, high-volume workflows

## Performance vs Readability

- **Application code**: Optimize for readability and dev speed
- **Backend and library code**: Can be lower-level and optimize for performance when working with thousands of objects

## Typing

- **Application code**: Rely on type inference where possible
- **Library code**: Provide full typing as appropriate

## Architecture Pattern

For moderate-sized features, organize code as:

1. **Main/orchestrating function**: Receives inputs, coordinates the workflow
2. **Data pipeline**: Transform data through a series of helper functions
3. **Helper functions**: Each performs one logical behavior chunk
   - Functions with logic can be unit-tested easily
   - Functions with side-effects are isolated

Main functions can be procedural and as long as needed. Helper functions should be focused and single-purpose. No fixed function length constraints.

## Code Organization

- Helper functions stay in the same file as the main/orchestrating function until there are 2-3+ helpers
- Extract logic that will likely be tested: data transformations, testable algorithms, pure business logic
- Keep side effects isolated for easier testing

## Configuration and Constants

- Hard-coded values belong in a constants file
- Configuration belongs in a config file
- Validate config before runtime to error on missing/invalid settings

## Critical Cases

When edge cases or error handling appear potentially critical, mention concerns in chat but don't write the code unless asked.
