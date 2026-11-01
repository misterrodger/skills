# Stage 4: Iterate

Fix type errors and test failures in rounds until every repo in the slice is green. Each round fixes errors at their source, then propagates and checks again.

Read [checklist-process.md](checklist-process.md), section "Stage 3-4".

## Each round

1. Run `type-check` and tests in every repo in the slice, and record the error counts.
2. For each type error, fix it at the highest level it can be fixed:
   1. **The contract or the DAO declaration.** Extend or correct the schema in `zod-contracts`, or the `.d.ts`, so it matches what the code does at runtime. Before adding a local type, look for an existing schema to extend.
   2. **An existing check.** Narrow inside a check the code already runs, e.g. add `|| !vehicle` to an existing `if (...) throw`.
   3. **A precise annotation.** Use a `@type {const}` literal, `jest.mocked(...)`, or the contract type on a parameter. Don't cast.
   4. **A new runtime guard, as a last resort.** It must not change behaviour. Record it in the slice note's guard table and tell the user.
3. Don't fix an error by widening a type (`| undefined`, `| string`, a new optional field, a `??` fallback), by adding `Pick`, `Omit` or `Partial`, or by loosening a schema. Any of these needs the user's approval.
4. **A file outside the slice was pulled into the check.** Run `npx tsc --explainFiles` to find which `require` brought it in, and cut that edge, for example by moving a constant. Don't type the out-of-scope file.
5. **A stage 0 test went red.** The slice changed behaviour. Revert to preserve it, or, if it is a correction already marked in the slice note, update the test in its own commit.
6. **A bug the types revealed.** Note it in "Bugs the typing found" and ask before fixing it if the fix is larger than the slice.
7. If the contracts or DAO changed, propagate again ([stack-map.md](stack-map.md)) before the next round.

If you're about to make a large fix, change runtime behaviour, or reach into another team's code, stop and ask first.

## Gate

- [ ] `type-check` reports 0 errors over each repo's `include`.
- [ ] The full test suites pass in every repo in the slice, including the stage 0 tests.
- [ ] Every guard added and every bug found is in the slice note, and the user has been told about them.
- [ ] Before and after error counts have been reported to the user.
