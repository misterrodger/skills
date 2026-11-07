# Stage 7: Tests and test data

Make the test data Zod-first, with a small set of shared fixtures and builders checked against the contracts. Tests should catch drift, and they shouldn't restate schemas. This stage can find contract gaps and loop back to stage 3.

Read [checklist-tests-and-fixtures.md](checklist-tests-and-fixtures.md), part "Stage 7", and [checklist-process.md](checklist-process.md), section "Stage 5-8".

## Steps

1. **Inventory the test data** for the slice across every repo: inline objects, builders, `tests/input/` files, mocks, and copies of the same entity.
2. **Consolidate.**
   - Contract-shaped entities, and builders for them, go to `connex-utils-node-v4/src/zod-contracts/<domain>/fixtures/*.ts`. They are exported from the fixtures subpath only, never from the domain index.
   - Handler-specific request and event inputs stay repo-local, built from the shared fixtures.
   - Merge near-duplicate builders.
   - If the slice is moving several sets of test data into shared typed fixtures, **ask the user** whether those builders should use seeded Faker.js. Otherwise keep fixed literal values.
3. **Type the builders** with this pattern:

   ```javascript
   /**
    * @param {Partial<Order>} [overrides]
    */
   const order = (overrides = {}) => {
     const base = /** @satisfies {Order} */ ({
       crn: 'o-1',
       primarySystemProductType: 'MORTAR',
       locationRef: 'loc-1',
     });
     return { ...base, ...overrides };
   };
   ```

   Static fixtures use `/** @satisfies {Type} */` with `@type {const}` (or `as const satisfies Type` in `.ts`). Prove the typing catches drift: misspell a property, remove a required one, confirm `type-check` fails, then revert.
4. **Fixture or contract?** When a fixture doesn't fit the contract, decide which side is wrong. Don't make a schema field optional or nullable just because a fixture lacks it. A schema fix loops back to stage 3.
5. **Update the tests:**
   - Assert on the fixture, or part of it, first, e.g. `expect(result).toStrictEqual(orderFixture.destination)`.
   - Otherwise use `toStrictEqual` with exact values.
   - Use `jest.mocked(...)`, with mock return values typed so that drift shows.
   - Delete tests that only restate a schema or re-test Zod.
6. **Type-check the tests.** Add the test and fixture files to the repo's `tsconfig.json` `include`. Fix their type errors in test code, unless the error shows a real contract gap, which goes back to stage 3.
7. **Self-review.** Go through every line of the stage 7 checklist against the test diff, record the findings in the slice note, and loop until none are left to fix now.
8. Run the full suites and `type-check` in every repo.

## Gate

- [ ] Shared fixtures and builders are in `zod-contracts/<domain>/fixtures`, and no production entry point imports them.
- [ ] Drift-catching has been checked in practice on at least one builder and one fixture.
- [ ] The test files are in `include`, and `type-check` passes.
- [ ] The stage 7 checklist has been checked, and all findings are resolved or logged.
- [ ] The full suites pass, including the stage 0 tests.
