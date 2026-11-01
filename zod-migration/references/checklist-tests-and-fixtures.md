# Checklist: tests and fixtures

Check every line against the diff, and record each finding as fix-now, ask John, or log.

Quotes and sources: ~/Github/planning/zod-migration-skill/FEEDBACK-TESTS-AND-FIXTURES.md

## Stage 0: safety-net tests

### Characterization / safety-net tests

- [ ] **T1.1** Before any change, every touched endpoint has route/API-level tests (ideally at least one integration test per endpoint) that pin current behaviour without judging it.
- [ ] **T1.2** The stage-0 report states whether route-level/integration tests exist, which handler logic paths are and aren't covered, and which AI-added logic could be removed (ASK: John before removing it).
- [ ] **T1.3** Before refactoring, existing tests are reviewed for behaviour coverage and tight, determinate assertions, then extended; Stryker runs locally (not CI) to close boundary gaps; coverage ships in its own PR first.
- [ ] **T1.4** For code already in production, the slice covers only endpoints/features that can be tested manually, and the diff extends automated coverage for what it changes.
- [ ] **T1.5** Integration-style tests mock external service calls with MSW and follow the shape of existing `-service` integration tests (e.g. cds-dispatch-service).
- [ ] **T1.6** The Swagger/OpenAPI document is generated before the change and regenerated after; the diff shows only descriptive-metadata changes, with structure unchanged.
- [ ] **T1.7** Contract errors are detectable through type-check and tests (with stubs/dummy data), without running the app by hand.
- [ ] **T1.8** Every finding that claims a crash or bug cites the exact location and, for runtime claims, comes with a test that reproduces it.

### Running and reporting tests

- [ ] **T9.1** Tests run through the repo's npm scripts (`npm test -- <path>`, `npm run test-individual -- <path>`, full suite `npm run test`), never `npx jest`.
- [ ] **T9.9** Every test that passed before the change still passes after it; a slice is not done while any previously passing test fails.

## Stage 6: tests and test data

### What not to test (and what to test)

- [ ] **T2.1** No tests that only restate a schema's shape or re-test Zod, framework behaviour or trivial helpers; the schema definition is the proof and documentation.
- [ ] **T2.2** Every `.transform` and real refinement logic in a Zod schema has a unit test; non-trivial primitives (e.g. `hoursTimeSchema`) have tests that act as documentation.
- [ ] **T2.3** No tests whose only job is to check that a typed fixture fits its schema or type; `as const satisfies` already guarantees that.
- [ ] **T2.4** No tests that only check constants, tuples or enum lists; parity tests between duplicated constants are removed once the constants share a single source.
- [ ] **T2.5** When a field is removed from a contract, tests asserting the deprecated field is rejected (e.g. a `rejects deprecated volumeUomCode` test) are deleted.
- [ ] **T2.6** Removing unused or defensive-only code also removes every reference to it, including its test file.

### Test structure

- [ ] **T3.1** Each changed test reads as a behavioural spec: Arrange-Act-Assert, exactly one behaviour, clarity over DRY.
- [ ] **T3.2** `it.each` is used only with several meaningful cases, and each test asserts its scenario-specific value (e.g. the canceled status, not a generic `ORDER_STATUS`).
- [ ] **T3.3** Test helpers contain no branching logic and no throw-as-control-flow.
- [ ] **T3.4** Schema/validation test data includes at least one valid object alongside the failing cases.

### Fixtures and builders

Sanctioned builder pattern (the overrides parameter is the only allowed `Partial`):

```js
/**
 * @param {Partial<Order>} [overrides]
 */
const order = (overrides = {}) => {
  const base = /** @satisfies {Order} */ ({
    crn: 'o-1',
    primarySystemProductType: 'MORTAR',
    locationRef: 'loc-1',
    destination: { address: {} },
    supplierStatus: { id: 'CONFIRMED', name: 'Confirmed', supplierStatusRef: 'status-1' },
  });
  return { ...base, ...overrides };
};
```

#### Shape and typing

- [ ] **T4.1** Every fixture and test-data object is typed `as const satisfies <Type>` (JSDoc: `/** @satisfies {Type} */` plus `@type {const}`), never plain `@type`; untyped test-data files are flagged. Already-narrow string constants need no `@type {const}`.
- [ ] **T4.2** `satisfies` targets a named type exported from `-utils` zod-contracts (or derived from one); test files, generators and builders add no large inline typedefs.
- [ ] **T4.3** Drift detection is proven by trying it: removing, misspelling or retyping a fixture, builder base or override property errors in the IDE and in `type-check`.
- [ ] **T4.4** Builders follow the pattern above: complete base checked with `@satisfies` against the real contract type, `@param {Partial<Type>} [overrides]`, `return { ...base, ...overrides }`; no other `Partial`/`Pick`/`Omit`; reshape by composing schemas in zod-contracts (prefer `.extend`).
- [ ] **T4.5** Fixtures and builders have no `@returns` annotations; their type comes from `satisfies` on the value.
- [ ] **T4.6** Builders contain no throws, guards or fallback defaults for misuse; they assume correct usage and rely on types to flag mistakes.
- [ ] **T4.7** Tests read narrowly typed fixture data directly by index or key, not with `.find`; no `as const` inside `expect(...)` and no explicit `readonly` clutter on test data.
- [ ] **T4.8** Shared fixtures model complete contract objects, not bare IDs, and are never typed `any`.
- [ ] **T4.9** DAO test files (e.g. `product.test.js`) type their data with the DAO's `.d.ts` types. ASK: trial it in one file and get John's review before rolling it out.

#### Location and packaging

- [ ] **T4.10** Contract-shaped test data duplicated across `-service`/`-exp`/`bm-yard` is consolidated into a small set of `.ts` fixtures and builders in `connex-utils-node-v4/src/zod-contracts/<domain>/fixtures`; plans list concrete consolidation opportunities.
- [ ] **T4.11** Shared fixtures are exported through their own sub-path entry point, and no production module imports that path.
- [ ] **T4.12** Generators live in the existing fixtures folder, not a new module. Builders use fixed literal values. ASK: when the slice moves several sets of test data into shared typed fixtures, ask John whether those builders should use seeded Faker.js.
- [ ] **T4.13** The initial `-utils` scaffolding PR creates the fixtures and constants folders empty with a `.gitkeep` and adds no fixture content.
- [ ] **T4.14** Handler-specific inputs stay repo-local and follow the repo's test-data tours (e.g. `backend/.tours/3-create-data-in-unit-tests.tour`, `6-unit-testing-standards.tour`), including builders in `tests/input/`.

#### Reuse

- [ ] **T4.15** Tests import existing shared fixtures (with `as const` applied where the fixture is defined) instead of copying them; repeated fixtures become shared builders that accept overrides.
- [ ] **T4.16** No two builders or test files do the same job (e.g. two `buildBaseJouneyPayload`, two `map-journey-db-item-to-response.test.js`); merge them or give them clearly distinct names.

#### Fixture vs schema mismatch

- [ ] **T4.17** No schema field is made optional/nullable just because a fixture lacks it; for each mismatch weigh extending the fixture against fixing the schema (back to the contract stage). ASK: John with a recommendation.

### Mocks

- [ ] **T5.1** Typed mocks use `jest.mocked(...)` as in the dispatch-service and driver-management-exp journeys work, not `jest.spyOn`; jest-mock-extended is not added (deferred).
- [ ] **T5.2** Values passed to `mockResolvedValue` and similar on DAO/HTTP mocks are type-checked against the real return type; no `jest.mocked(...)` result resolves to `any` (ASK: John if one cannot be typed).
- [ ] **T5.3** Required schema fields (e.g. `recordType`) are always provided in mocks and test data; no code or mock falls back for them being missing.

### Assertions

- [ ] **T6.1** Assertions use exact, deterministic values (freeze time and inputs where needed), not `expect.any(...)`, loose bounds like `toBeLessThan`, or `typeof` checks.
- [ ] **T6.2** Use `toStrictEqual`, not `toEqual` (`vitest/prefer-strict-equal` where configured); no `rejects.toBeTruthy` or path-only smoke tests; rejections and errors assert their typed shape.
- [ ] **T6.3** Assert on the fixture or part of it first (e.g. `toStrictEqual(orderFixture.destination)`), then `toStrictEqual` with exact values; snapshots only for large characterization bodies, plus direct contract-critical assertions; no `toMatchObject`.

### Type-checking tests

- [ ] **T7.1** Test files are type-checked through the repo's single `tsconfig.json` with tests in its `include`; no `tsconfig.test.json`, no `strict: false`, and one type-check script in package.json.
- [ ] **T7.2** Test globals (`describe`, `it`, `expect`) are typed via tsconfig `types` (jest types or vitest globals), not per-file imports or suppressions, so matchers like `toBe` type-check.
- [ ] **T7.3** Test type errors are fixed only in test, fixture, mock and builder files; production types are not weakened and production type-check stays at 0 errors.
- [ ] **T7.4** Each `@ts-expect-error` sits on a valuable invalid-input case, carries an explanation, and suppresses a real error (removing it fails type-check); ineffective ones are removed.
- [ ] **T7.5** Tests contain no `throw` added to narrow types and no `if (!x) return;` guards that silently skip assertions; they assert or rely on correct types.
- [ ] **T7.6** No `@template` generics are added to test files or test helpers to satisfy the type-checker.
- [ ] **T7.7** Changed test files have zero IDE/type-check errors, including module-export errors and values imported where a type is needed.
- [ ] **T7.8** No type-helper or boundary-type files are added under test folders (e.g. `test/boundary`); they sit beside the production code.

### Imports in tests

- [ ] **T8.1** Tests inside packages such as `connex-utils-node-v4` import source, never `dist` (zod-contracts tests may be `.ts`); consumer repos import the published `zod-contracts/dist/<domain>` sub-path.
- [ ] **T8.2** Node built-ins are imported with the `node:` prefix (e.g. `node:crypto`) in tests and in the code they cover.

### Running and reporting tests

- [ ] **T9.2** New test setups use Vitest (its coverage, globals, tests colocated with the file tested); existing Jest repos stay on Jest; check which runner `zod-contracts` uses rather than assume.
- [ ] **T9.3** Relevant tests and type-check run locally before handoff (targeted only when John says the full run is too slow); changes stay uncommitted for John to review, never committed or pushed.
- [ ] **T9.4** Before finishing, confirm the intended files are all present with nothing extra, re-run tests and type-check, and report before/after type-error counts (e.g. 232 to 0).
- [ ] **T9.5** Cross-repo changes are tested by copying local `dist` builds from `-utils` to `-dao` to app `node_modules`, without editing consumer package.json versions or publishing; never `npm install`/`npm ci` over them.
- [ ] **T9.6** Each of the 2-4 phased PRs is self-contained, implements only the requested behaviours, and carries tests for them.
- [ ] **T9.7** Plans, implementations and a separate self-review pass are checked against `/test-code-quality`, alongside `/dev-coding-practices`, `/typescript-type-safety` or `/jsdoc`, and `/pr-review`.
- [ ] **T9.8** When a test issue is flagged in one file (e.g. ineffective `@ts-expect-error`, generics, `throw`), the same pattern is searched for and fixed across all touched files and repos.
