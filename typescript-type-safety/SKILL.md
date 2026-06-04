---
name: typescript-type-safety
description: Opinionated rules for writing strict, concise, type-safe TypeScript and for setting up the tsconfig/ESLint config that enforces it. Use this whenever writing, reviewing, refactoring, or configuring TypeScript or TSX — including React components, Node services, and shared libraries — even when the user doesn't explicitly say "type safety." Trigger it for any request that involves .ts/.tsx files, typing decisions (any vs unknown, type vs interface, generics, unions, narrowing), validating external/API data, or setting up tsconfig, ESLint, or type tests. Composes with dev-coding-practices; this skill governs the type system specifically.
---

# TypeScript Type Safety

Goal: a strict, concise, genuinely useful type layer — types that catch real bugs and document intent without ceremony. This composes with **dev-coding-practices** (functional-lite, concise, fail-fast, `undefined` over `null`, inference in app code / full typing in library code). Where they overlap, that skill's style rules still hold; this one governs the type system.

## Core stance

- **Make illegal states unrepresentable.** Model with unions so bad combinations can't be constructed, rather than validating them away later.
- **Declare at boundaries, infer inside.** Annotate signatures, public APIs, and object literals that must match a known shape. Let locals, simple returns, and generic instantiation infer. Assert (`as`) only as a last resort — it overrides the checker instead of consulting it.
- **Keep it simple first.** Prefer the plain solution (separate functions, call-site iteration) over clever generics/overloads. Reach for the heavy machinery only in library code, where extra complexity buys consumers tighter safety.
- **Concise.** The type layer should clarify, not bury the code. No annotation that inference already provides correctly; no abstraction without a second caller.

## Authoring rules

Apply these by default when writing or reviewing TS:

- **Never `any`. Use `unknown` and narrow.** `any` silently disables checking and spreads. If forced, `// @ts-expect-error` with a reason beats `any` because it's scoped and self-documenting.
- **`const`, not `let`**, unless reassignment is real. `const` preserves the narrow type; `let` widens.
- **`type`, not `interface`.** Compose with `&` and `|`. Use `interface` only when you specifically want declaration merging (rare).
- **Model with discriminated unions, not bags of optionals.** `{ ok: true; data: T } | { ok: false; error: string }` over `{ ok: boolean; data?: T; error?: string }`. The discriminant forces every consumer to handle each case.
- **Exhaustiveness via `assertNever`.** In the `default` of a switch over a union, call a helper that throws — compile-time *and* runtime safety:
  ```ts
  function assertNever(x: never): never {
    throw new Error(`Unhandled case: ${JSON.stringify(x)}`)
  }
  ```
- **Validation = boolean type predicate by default** (`(x): x is T`). It branches cleanly and composes with `filter`. Use a throwing assertion function (`asserts x is T`) only when an invalid value means you can't continue. Use a **branded type** only when the *validated-ness* must persist downstream — it's a different tool, not a default.
- **`readonly` / `as const` for immutable data.** `as const` is deep; `Object.freeze` is shallow. Derive types from constants: `keyof typeof o`, `(typeof o)[keyof typeof o]`, `arr[number]`.
- **`satisfies` to check a literal without widening** — config objects, tightening loose lib types (`{…} satisfies T`). Plain annotation widens; `as const satisfies T` checks *and* keeps readonly literals.
- **`import type { … }`** for type-only imports (enforced by `verbatimModuleSyntax`).
- **Prefer `key: T | undefined` to `key?`** when you want the compiler to force handling of the absent case at every use site.

## Validate at the boundary

Anything entering from outside the type system is **not** the type you wish it were — type it `unknown` and validate before use. Treat as untrusted: `fetch`/API responses, `.json()` and `JSON.parse`, form input, `localStorage`/`sessionStorage`, URL/query params, webhook payloads, DB/object-store/filesystem reads. Validate with a schema (Zod) at the edge and let the parsed type flow inward. `ts-reset` makes the stdlib honest here (`JSON.parse` → `unknown`, etc.) — see `references/setup.md`.

## Functions, generics, overloads

- Default to **separate, single-purpose functions** over overloads.
- Want one helper to take slightly different inputs and return correspondingly different types? Don't encode that with overloads/generics — do the `map`/`filter` at the **call site** and let the helper be a single predicate/transform. Correct narrow types, simpler code.
- Use **generics to express a relationship** (input type drives output, or two params vary together) — mainly in shared/library code. In app code, prefer the call-site approach first.
- TSX: write `<T,>` (trailing comma) so the param isn't parsed as JSX.

## React (when .tsx is involved)

- Style: `React.CSSProperties`. (MUI: `style` accepts it, but `sx` is MUI's own `SxProps<Theme>` — don't force `CSSProperties` there.)
- `children: React.ReactNode`; narrow to `React.JSX.Element` only if a single element is required.
- Wrap an HTML element with `ComponentProps<'button'> & { /* extra */ }`. In React 19 `ref` is a normal prop already included by `ComponentProps` — no `forwardRef`, and the `…WithRef`/`…WithoutRef` split is legacy.
- Setter prop: `React.Dispatch<React.SetStateAction<T>>`.
- Hooks: `useState` infers from initial value, else `useState<T>()`; `useState<T | undefined>(undefined)` for async data. `useRef<HTMLInputElement>(null)`. For `useContext`, create as `createContext<T | undefined>(undefined)` and wrap reads in a custom hook that throws outside a provider, so consumers get a clean non-`undefined` `T`.
- Event handlers type themselves inline; to extract one, read the inferred type (e.g. `React.ChangeEventHandler<HTMLInputElement>`) and annotate.

## Enforcement (do this when setting up or auditing a repo)

The configs that make the above non-optional live in `references/`:

- `references/tsconfig.base.json` — `strict` plus the high-value extras (`noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `verbatimModuleSyntax`, …).
- `references/eslint.config.mjs` — `strictTypeChecked` + `stylisticTypeChecked`, with overrides for the house style (notably `consistent-type-definitions: 'type'`, since the stylistic preset defaults it to `interface`).
- `references/setup.md` — install, ts-reset, scripts, CI, and plain-JS adoption.

When asked to set up or tighten a project: read those three, copy the configs in, wire the `typecheck` / `lint` / `test` scripts into a `ship` script and required CI checks. Gate types in CI with `tsc --noEmit`.

## When to relax

- **App vs library:** in app code lean on inference and keep annotations light; in library code annotate public surfaces fully and emit `.d.ts`.
- **Tests:** the ESLint config already loosens `no-explicit-any` / `no-unsafe-*` / non-null assertions in test files — mirroring real-world mocking needs.
- **Type tests:** for library code, lock the public types with `expectTypeOf` (Vitest) and `@ts-expect-error` so a type regression fails CI.

Don't add strictness theatre. Each rule here earns its place by catching a real class of bug or removing a real ambiguity; if a rule only generates noise in a given codebase, turn it off deliberately rather than littering inline disables.
