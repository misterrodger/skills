---
name: documentation
description: Documentation practices for code, PRs, and technical communication. Use when completing features, reviewing code, or preparing for PR.
---

# Documentation

## Philosophy

Code is the primary documentation. Write docs that add value, not noise.

## Code Comments

- Code should be self-documenting — good names, clear structure
- Type definitions as documentation — well-typed code is self-documenting
- Add comments only when they add value: why, not what
- Complex business logic, non-obvious decisions, workarounds — worth a comment
- Decision context: when code looks wrong but is intentional, explain why — saves future dev from "fixing" it

## Inline Examples

- For utilities or complex functions, a usage example in the docstring beats paragraphs of explanation

## README

- Update README when adding features, changing setup, or altering usage
- Keep it current — stale docs are worse than no docs

## Changelog

- Maintain CHANGELOG.md for user-facing changes
- Follow Keep a Changelog format

## API Documentation

- Document public APIs — endpoints, params, responses, errors
- Use OpenAPI/Swagger for REST
- Keep in sync with code

## Deprecation Notices

- Mark deprecated code clearly
- Include: why, when it will be removed, what to use instead

## Technical Diagrams

- Suggest a diagram when feature involves: multiple services, complex data flow, state machines, or non-trivial architecture
- Ask: "Would a diagram help the next dev understand this faster?"

## Engineering Documents

- Suggest a technical doc for: significant new features, architectural decisions, complex integrations
- ADRs (Architecture Decision Records) for decisions worth preserving

## Onboarding Context

- For complex domains, a brief "concepts" or "glossary" doc helps new devs ramp up

## PR Description

- Suggest PR description content: what changed, why, how to test
- Link to relevant tickets/issues
- Call out anything reviewers should focus on