# Stage 1: Scope

Choose the smallest chunk that is worth doing, show the user where its edges are, and **stop until the user confirms it**.

Read [checklist-process.md](checklist-process.md), section "Stage 0-1".

## Steps

1. **Trace the candidate across repos.** For each resource, find:
   - its contracts in `zod-contracts/<domain>` (existing or missing)
   - the DAO functions and `.d.ts` signatures it uses
   - the `-service` handlers and their JSON schemas
   - the `-exp` BFF handlers and JSON schemas
   - the frontend modules that consume it
   - any `cds-company-admin` or `cds-setup-service` source schemas or handlers for the same entity
   - other consumers such as `cds-bm-yard` and `cds-resource-scheduler`

   Use `rg` across `~/Github/Command_Alkon`.
2. **Find local types.** List the types, typedefs and schemas defined in `-service`, `-exp` or frontend files for this resource. For each, say whether an existing `zod-contracts` schema could be extended instead.
3. **Check release status.** Is the code released, in production use, or still dark or unreleased? Is the object a widely used canonical entity on a hot path? This is evidence for stage 2's strictness questions. It isn't a decision.
4. **Propose the slice.** Give the repos, files and handlers in scope, and what is explicitly next door and staying legacy. Keep it to one resource, or a few tightly coupled ones. In a large service such as dispatch, keep the slice narrow.
5. **Flag new domains.** If the slice needs a `zod-contracts` domain that doesn't exist yet, say so. Creating one needs the user's approval.
6. **Ask.** Present the proposal and its alternatives (narrower or wider) using `AskQuestion`, then stop.
7. **Write the slice note** from [slice-note-template.md](slice-note-template.md), with the confirmed scope and the stage 0 behaviour table.

## Gate

- [ ] **The user confirmed the slice**, and any new domain.
- [ ] The slice note exists, with scope, out-of-scope items and behaviours.
- [ ] Stage 0 tests cover everything in the confirmed scope. Add any that are missing before moving on.
