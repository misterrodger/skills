# Stage 3: Implement and propagate

Make the changes top-down, from the contracts to the DAO to the apps, and copy the builds locally so every repo type-checks against the new contracts.

Read [checklist-process.md](checklist-process.md), section "Stage 3-4", and [stack-map.md](stack-map.md), sections "Local propagation" and "checkJs island".

## Steps

1. **Contracts (`connex-utils-node-v4`).**
   - Write the schemas from the stage 2 plan in `src/zod-contracts/<domain>`.
   - Export them inline from the domain `index.ts`, and infer the types from the schemas.
   - Any non-strict schema gets the approved code comment. Constants go to their confirmed homes.
   - Add tests only for logic: transforms, refinements, and non-trivial primitives.
   - Run `npm run build:zod-contracts` and `npm test`.
2. **Propagate the contracts** into `connex-dao-node-v4` and every app repo in the slice ([stack-map.md](stack-map.md)).
3. **DAO (`connex-dao-node-v4`).** Replace `object` and loose types in the `.d.ts` files with contract-derived types. Leave the `.js` runtime alone unless the plan says otherwise. Run `tsc --noEmit` on the changed `.d.ts` files and `npm test`.
4. **Propagate the DAO** into every app repo in the slice.
5. **Turn on checking for this iteration.**
   - If the app repo has no `tsconfig.json`, create one from the [stack-map.md](stack-map.md) template, with a `type-check` script.
   - Add the files you're about to type to `include`, now and not before.
   - Don't widen `include` to cover a dependency that is out of scope.
6. **Apps.**
   - Replace local types with `@import` from the contracts and the DAO.
   - Parse at the boundary with the imported shared schema, using `parse` where the existing error mapper owns the response and `safeParse` where the handler turns a failure into a specific result.
   - Move the BFF onto the same shared schema.
   - Delete hand-written validation and local schemas that the contract now covers.
   - Keep inner functions receiving what they did before, unless the plan says otherwise.
7. **Run** `type-check` and tests in every repo, then go to stage 4.

Keep schema moves and on-purpose behaviour corrections in separate commits, so the schema commit reads as "same responses, new contract source". Don't commit unless the user asks.

## Gate

- [ ] The contracts build, and the `-utils` tests pass.
- [ ] The copied `dist` was checked in the DAO and in each app, including any nested copies.
- [ ] Each app repo in the slice has its `tsconfig.json` and its updated `include`.
- [ ] The stage 0 tests have been run. Red tests are handled in stage 4.
