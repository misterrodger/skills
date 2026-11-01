# Stack map

Command Alkon specifics. Paths are under `~/Github/Command_Alkon`. Check package scripts before relying on them, because they drift.

## Repo roles

| Role | Repo | Notes |
| --- | --- | --- |
| Contracts | `connex-utils-node-v4` | Zod 4 TypeScript in `src/zod-contracts/<domain>/*.ts`, compiled by `npm run build:zod-contracts` to `src/zod-contracts/dist`. Jest tests in `src/zod-contracts/tests/*.test.ts`. Legacy constants in `src/constants` |
| DAO | `connex-dao-node-v4` | `src/dao/<entity>.js` plus `<entity>.d.ts`. The `.d.ts` file owns the types. Don't repeat JSDoc in the `.js`. It is a type-only consumer, so it doesn't install `zod` |
| Domain service | `cds-*-service/backend` | Handlers in `v4/<resource>/<operation>/`, each with an `api-docs.js`. JSON schemas registered in `v4/schemas/register.js` and validated with `API.ValidateSchema` |
| Experience app | `cds-*-exp/backend` (BFF), `cds-*-exp/frontend` (React) | The BFF has its own JSON schemas. It moves to the same shared Zod schema in the same slice |
| Shared setup and admin | `cds-setup-service`, `cds-company-admin` | Source JSON schemas for Setup entities, in `backend/v4/<entity>/schemas`. About 6-10% of each repo is Scale Ticketing |
| Other consumers | `cds-bm-yard`, `cds-resource-scheduler`, `cds-dispatch-service`, `cds-driver-management-exp`, waste-compliance repos | Already partly migrated. Use them as patterns |
| API docs | `connex-api-node-v4` (`src/api-docs/openapi3`) | `OpenAPI3.initialize`, `getSpecificationDocs`, `validateApiSchema`, `publishApiSchema`. Also `api-docs/validate-api-doc` and `api-docs/publish-api-doc` for a supplied document |

## Imports

```javascript
// production: one domain subpath
const { laneSchema } = require('connex-utils-node-v4/zod-contracts/dist/bulk-materials');
// tests only: fixtures subpath, never imported by production code
const { laneFixture } = require('connex-utils-node-v4/zod-contracts/dist/bulk-materials/fixtures');
```

```javascript
/** @import { Lane } from 'connex-utils-node-v4/zod-contracts/dist/bulk-materials' */
```

`@import` goes at the top of the file, and the type is attached with `@type` or `@param`. `.d.ts` files import types from the same subpath.

## Scripts per repo

| Repo | Type-check | Tests | API docs |
| --- | --- | --- | --- |
| `connex-utils-node-v4` | `npm run build:zod-contracts` (runs `tsc`) | `npm test` (Jest) | n/a |
| `connex-dao-node-v4` | `npx -p typescript tsc --noEmit <changed .d.ts>` | `npm test` | n/a |
| `cds-bm-yard/backend` | `npm run type-check` | `npm test` | n/a |
| `cds-bulk-materials-service/backend` | `npm run type-check` | `npm test` | `generate-api-schemas`, `validate-api-schemas`, `publish-api-doc` |
| `cds-dispatch-service/backend` | `npm run type-check` | `npm test` | as above |
| `cds-waste-compliance-service/backend` | `npm run type-check` (`jsconfig.json`) | `npm test` (Vitest) | `validate-api-schemas` and `publish-api-doc` on the Zod document |

Always run through the npm scripts, never `npx jest`. TypeScript is run through `npx -p typescript@<version>` in repos that don't depend on it. Don't add `typescript` as a dependency.

## Local propagation

Don't edit `package.json` versions. Copy the build output over the installed package, and don't run `npm install` afterwards, because that would overwrite the copy.

1. **Contracts:** in `connex-utils-node-v4`, run `npm run build-and-copy-to <app-repo>`. That runs `build:zod-contracts` and `build-for-copy`, then copies `build/dist/` to `../<app-repo>/backend/node_modules/connex-utils-node-v4`. Repeat it for each app repo in the slice.
2. **Into the DAO:** `connex-dao-node-v4` has no `backend/`, so copy by hand after step 1: `cp -R build/dist/ ../connex-dao-node-v4/node_modules/connex-utils-node-v4`.
3. **DAO into the apps:** in `connex-dao-node-v4`, run `bash scripts/copy-local.sh <app-repo>`, which targets `backend/node_modules`. `build-for-copy.sh` calls `generateNpmCredentials`, which needs an AWS session. If that fails, build the folder by hand (`index.js`, `package.json`, `README.md`, `src/*` into `build/dist`) and copy that.
4. **Nested copies:** check for `node_modules/connex-dao-node-v4/node_modules/connex-utils-node-v4` in each app. If it exists, copy the contracts there as well.
5. **Frontend:** if a frontend imports the contracts, copy into `frontend/node_modules/connex-utils-node-v4` too.

Verify each copy by grepping the copied `dist` for a symbol you just added.

## checkJs island

Each app repo has one `tsconfig.json` with `allowJs`, `checkJs`, `noEmit` and the strict flags. Copy the flags from `cds-bm-yard/backend/tsconfig.json`: `strict`, `noUncheckedIndexedAccess`, `noImplicitReturns`, `noUnusedLocals`, `noUnusedParameters`, `maxNodeModuleJsDepth: 0`, `skipLibCheck`, and `types` set to the test runner plus libraries. `include` is an explicit list of the slice's files, with globs only where a whole folder is typed. Don't use per-file `// @ts-check`.

## OpenAPI pieces

| Piece | Where |
| --- | --- |
| Legacy spec | `OpenAPI3.initialize(require('../specification-params'))`, then `await OpenAPI3.getSpecificationDocs({ publicApisOnly: false })` |
| Legacy JSON schemas | `backend/v4/schemas/register.js`, and the `generate-api-schemas` output in `v4/api-docs/schema-type-defs.js` |
| Route discovery | `findApiResources` reads every `api-docs.js`. Keep those files, for discovery fields only |
| Zod document | `backend/v4/schemas/openapi-document.js` calls `createDocument` from `zod-openapi` (pattern: `cds-waste-compliance-service`) |
| Validate and publish a supplied document | `connex-api-node-v4/api-docs/openapi3/api-docs/validate-api-doc` and `publish-api-doc` (pattern: waste-compliance `scripts/`) |
| Existing doc test | `cds-waste-compliance-service/backend/tests/openapi-spec.test.js`. It hard-codes its operation map, whereas the drift test in stage 7 discovers operations by glob |
