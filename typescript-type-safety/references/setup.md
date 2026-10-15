# Setup & enforcement

## 1. Install

```bash
# Type checker + linter
npm i -D typescript eslint @eslint/js typescript-eslint
# Optional: stop ESLint and Prettier fighting over formatting
npm i -D prettier eslint-config-prettier
# Runtime validation at boundaries + stdlib fixes
npm i zod
npm i -D @total-typescript/ts-reset
# Type-level tests (also your unit runner)
npm i -D vitest
```

If using Prettier, append `eslintConfigPrettier` as the **last** item in `eslint.config.mjs` so it disables conflicting stylistic rules.

## 2. Drop in the configs

- Copy `tsconfig.base.json` to the repo root and `extends` it from each package's `tsconfig.json`, overriding `lib` / `jsx` / `module` per runtime (see the notes in that file).
- Copy `eslint.config.mjs` to the repo root.

## 3. Turn on ts-reset

Create `reset.d.ts` at the project root (include it via `tsconfig`):

```ts
import '@total-typescript/ts-reset'
```

This makes `JSON.parse` / `.json()` / `Array.isArray` return `unknown` instead of `any`, fixes `.filter(Boolean)` narrowing, and relaxes over-strict `.includes` on `as const` arrays.

## 4. Scripts

```jsonc
// package.json
{
  "scripts": {
    "typecheck": "tsc --noEmit",
    "lint": "eslint .",
    "test": "vitest run",
    "test:types": "vitest run --typecheck",
    "ship": "npm run typecheck && npm run lint && npm run test"
  }
}
```

Run `npm run ship` locally before pushing, and run `typecheck` + `lint` + `test` as **required** CI checks. Typed linting asks TypeScript to build first, so it's slower than plain ESLint — budget for it in CI.

## 5. Plain JS (gradual adoption)

For `.js` files you aren't converting yet: add `// @ts-check` at the top of a file, or a `jsconfig.json` with `"checkJs": true` to opt in project-wide. Annotate with JSDoc and pull in real types via `/** @type {import('./types').Foo} */`. The same `tsc --noEmit` gate covers these.
