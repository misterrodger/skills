# Stage 0: Safety net

Get the code you are about to change under tests at a seam, before any schema edit. These tests are the evidence that later stages kept behaviour the same. The method comes from Michael Feathers, *Working Effectively with Legacy Code*.

Read [checklist-tests-and-fixtures.md](checklist-tests-and-fixtures.md), part "Stage 0", and [checklist-process.md](checklist-process.md), section "Stage 0-1".

## Steps

1. **Read what exists.** Read the earlier slice notes in `~/Github/planning/zod-fullstack-type-safety/slices/`, the team migration doc, and the open PRs in `connex-utils-node-v4` and `connex-dao-node-v4` that touch this domain (`gh pr list`). Don't redo work that is already in flight.
2. **Name the observable behaviour** for each candidate resource: HTTP status and body, published event, DAO write, a calculated value, or a UI value.
3. **Find the seam.** Prefer one that already exists: the route or handler boundary first, then the DAO call, then a pure calculation.
4. **Gap analysis.** List the existing tests for each endpoint and handler. Every endpoint the slice will touch needs at least one route/API-level test that calls it and asserts the response. Where they exist, use the repo's tours (`backend/.tours/*`) for how to build test data.
5. **Write the characterization tests.** Record what the code does today, including odd compatibility behaviour. Mock external services at the network edge. For a large response body, a snapshot is acceptable only if the test also asserts the contract-critical fields directly.
6. **Mark each behaviour** in the slice note as preserve, correct on purpose, or later ticket. A characterization test is evidence of current behaviour, not a promise to keep it forever.
7. **Run the full suite** in each repo you'll touch, and record the baseline: pass and fail counts, and existing `type-check` error counts.

Scope isn't confirmed until stage 1. In stage 0, characterize the candidate area broadly enough to make scoping safe, then trim to the confirmed slice.

## Gate

- [ ] Every endpoint and handler likely to be in the slice has a route/API-level test that asserts the response.
- [ ] Each behaviour is marked preserve, correct, or later in the slice note.
- [ ] The new tests pass against unchanged production code.
- [ ] Baseline test and `type-check` results are recorded.
- [ ] The user has seen the list of tests added. Committing them is the user's call.
