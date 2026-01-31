---
name: ui-code-quality
description: UI component quality, accessibility, testing, and state patterns. Use when building, reviewing, or refactoring UI components in React/frontend codebases.
---

# UI Code Quality

## Philosophy

Semantic, accessible, testable. Components stay dumb. Logic stays extractable. URL is truth.

## A11y & UX

- Use semantic elements (`nav`, `main`, `article`, `button`, etc.)
- ARIA only when semantics alone aren't enough
- Validate keyboard navigation works
- Apply sensible focus management (mention when you've handled it)
- Client-side validation — tell users before they hit the server
- Optimistic UI updates — ask about case-by-case (pairs with TanStack Query stale time)

## Component Architecture

- **Page layouts as separate components** — children passed in
- **Custom hooks** — extract when reusable or to keep components dumb
- **Business logic in hooks** — testable separately from UI
- **Components stay presentational** — receive data, render, emit events
- **Watch for memory leaks** — cleanup `setTimeout`, `setInterval`, subscriptions

## Cross-Cutting Concerns

Auth, compliance (anonymisation, data masking, etc.) live in a separate service/folder with their own test suites.

## Loading & Error States

- **Skeletons over spinners** — always
- **All reasonable states covered**: loading, error, success, empty

## UI Testing Strategy


| What | How |
|------|-----|
| Components | Storybook stories — all states |
| Component interactions | Storybook interaction tests — for business/custom logic, not library behavior |
| Custom hooks | Jest unit tests |
| Business logic | Jest unit tests |
| API mocking | Mock Service Worker (MSW) |
| E2E | Playwright — happy-path acceptance tests, use high-level snapshot function |
| A11y | Separate test suite — includes keyboard nav |

No Jest DOM simulation for components. Interaction tests in Storybook keep E2E lighter.

## State Management

- **Avoid global state** — reach for it last, not first
- **Hooks over Context** — Context only for true cross-cutting concerns (theme, auth, i18n)
- **TanStack Query style** — re-fetch often, cache via query keys
- **Query keys in one file** — colocate, don't scatter
- **Ask about**: stale time defaults, optimistic updates (case-by-case)
- **URL as state** — filters, pagination, UI state in URL where possible
- **Avoid prop drilling** — query keys + cache beat passing data down

## Input Safety

- Check buffer sizes on inputs to avoid overflow

## Responsive

- Desktop-first
- Ask if mobile support is needed before building it

## Storybook

Every component gets a story. Every story covers:
- Default/success state
- Loading (skeleton)
- Error
- Empty
- Edge cases as needed

Use MSW handlers for data states.