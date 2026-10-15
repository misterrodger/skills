---
name: jsdoc
description: Emulates strict TypeScript checking in vanilla JavaScript with checkJs, JSDoc, and Zod-derived types. Use when editing .js under checkJs, adding or repairing JSDoc, creating Zod schemas or .d.ts contracts, resolving type-check errors, or deciding where a type should live.
---

# JSDoc

Emulate modern, strict TypeScript checking in a predominantly vanilla JS codebase. Use `checkJs`, Zod-derived types, and JSDoc. Do not rewrite the file to TypeScript to get the check.

See the typescript-type-safety skill for other general type practices. Representative `checkJs` configs are in [tsconfig.md](tsconfig.md).

## Core rules

- Rely on Zod schemas and derived types as the single source of truth wherever possible. Those types are then added through DAO and both of these imported as appropriate into application code directly.
- Prefer to update types in Zod-first or other upstream libraries/SDKs rather than application code. Try to avoid mutating types in application codebase.
- App vs library: 
  - in application code primarily import schemas/types from the SDKs, lean on inference and keep annotations light, and keep any local type definitions minimal and only if really necessary
  - in library code annotate public surfaces fully and emit `.d.ts`.
- Libs using .d.ts should keep the JSDoc types and comments fully in the .d.ts file, don’t duplicate in .js file.
- Preferably migrate hand-written types in .d.ts to zod-contracts when possible.
- Keep types simple. Derive them from a Zod schema or a simple type definition. Avoid generics, overloads, and similar machinery. Prefer a simpler pattern, even if less concise.
- Type utils like `Pick`, `Omit`, and the rest are a code smell. Not necessarily wrong, but double-check. They may unintentionally weaken the types or lead to drift and errors. Prefer instead to update the type source of truth (Zod or other type definition at the source) rather than modifying it downstream in another module.
- Put `@import` at the top of the `.js` file only, the way a TypeScript file imports types. Use `@type` to attach an imported type. Do not restate a signature the declaration already owns.
- `/** @type {const} */` is `as const`. Pair it with `/** @satisfies {MyType} */` when a constant or fixture must match a type without widening.
- Changed files must be inside the active `tsconfig.json` `include`. Editor diagnostics are not the CI check. Do not widen that island to type an out-of-scope dependency. ESLint `strictTypeChecked` does not replace `tsc --noEmit`.
- Run the repo type-check, then targeted tests.

## Type ownership

zod-contracts in the utils package (`connex-utils-node-v4/zod-contracts`) is first. It is the top of the hierarchy. Import those types into the DAO package, domain-specific SDKs, and application code.

If there isn’t a domain entry yet in zod-contracts, ask whether now is a good time to add one, or else where to put any new or updated types in the codebase you are working on.

## Zod, DAO, application

Schema and inferred type, in zod-contracts:

```ts
export const listJourneysRequestSchema = z
  .object({
    entityRef: z.string().min(1),
    date: z.string(),
  })
  .strict();

export type ListJourneysRequest = z.infer<typeof listJourneysRequestSchema>;

export const storedJourneySchema = z
  .object({
    crn: z.string().min(1),
    entityRef: z.string().min(1),
    date: z.string(),
  })
  .strict();

export type StoredJourney = z.infer<typeof storedJourneySchema>;
```

DAO adds that type to its boundary. The shape stays in zod-contracts:

```ts
import type { ListJourneysRequest, StoredJourney } from 'connex-utils-node-v4/zod-contracts/dist/journeys';

export function listJourneys(request: ListJourneysRequest): Promise<StoredJourney[]>;
```

Application code imports the schema for a runtime parse and the type for a helper. `@import` stays at the top of the file:

```js
/** @import { ListJourneysRequest } from 'connex-utils-node-v4/zod-contracts/dist/journeys' */

const { listJourneysRequestSchema } = require('connex-utils-node-v4/zod-contracts/dist/journeys');

const listJourneys = async request => {
  const input = listJourneysRequestSchema.parse(request);
  return toQuery(input);
};

/** @param {ListJourneysRequest} request */
const toQuery = request => request.date;
```

Require DAO the same way the package exports it (`require('connex-dao-node-v4')`). Its `.d.ts` already carries the zod-contracts types, so the `.js` implementation does not repeat them.

Planned, not the current default:

- DAO consumes the Zod schema and validates reads and writes, so application code receives the inferred type.
- API handlers parse requests and responses with the same schemas.
- JSON API/OpenAPI schemas may be replaced with Zod-first `createDocument` from `zod-openapi`.

Ask before doing this in the code the user is working on.

## Typed constants/fixtures, tests and test builders

```js
const STATUSES = /** @type {const} */ (['OPEN', 'CLOSED']);

/** @satisfies {ListJourneysRequest} */
const FIXTURE = /** @type {const} */ ({
  entityRef: 'entity-1',
  date: '2026-05-08',
});

/**
 * @param {{ crn: string, entityRef: string, date?: string }} params
 * @returns {StoredJourney}
 */
const buildStoredJourney = ({ crn, entityRef, date = '2026-05-08' }) =>
  /** @satisfies {StoredJourney} */ ({
    crn,
    entityRef,
    date,
  });

/**
 * @param {Partial<StoredJourney>} [overrides]
 * @returns {StoredJourney}
 */
const buildStoredJourneyWithDefaults = (overrides = {}) => ({
  .../** @satisfies {StoredJourney} */ ({
    crn: 'journey-1',
    entityRef: 'entity-1',
    date: '2026-05-08',
  }),
  ...overrides,
});
```

`@satisfies` checks the generated object. An explicit parameter type or `Partial<TheType>` checks call-site names, so a missing or misspelled field is a type error in the IDE.

**Type tests:** for library code, lock the public types with `expectTypeOf` (Vitest) and `@ts-expect-error` so a type regression fails CI.
