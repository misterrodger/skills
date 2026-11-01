# Stage 5: Self-review

This is a separate pass over your own diff, made after implementation and before tests and OpenAPI. Its checklist was compiled from past review feedback, so a finding here is something the user would otherwise flag.

Read [checklist-schemas-and-types.md](checklist-schemas-and-types.md), all of it, and [checklist-process.md](checklist-process.md), section "Stage 5-7".

## Steps

1. Collect the diff in every repo in the slice: `git diff` and the untracked files.
2. Go through **every line** of [checklist-schemas-and-types.md](checklist-schemas-and-types.md) against that diff. Don't skip sections that seem not to apply. Confirm that they don't.
3. Look specifically for:
   - **Local types and schemas** left in `-service`, `-exp` or frontend files that an existing contract could replace or extend.
   - **Transforms** still in app code that belong in the contract as `.transform` with `z.input` and `z.output`.
   - **Constants** duplicated across repos.
   - **Pick, Omit and Partial** downstream, outside the sanctioned builder `overrides`.
   - **Non-strict schemas**, each with an approval, a code comment and a ledger row.
   - **DAO signatures** that are still `object` or broader than runtime behaviour.
4. Record each finding in the slice note's findings log as one of:
   - **fix now:** in scope, with a clear fix.
   - **ask the user:** a judgement call, or something outside the slice.
   - **log:** a follow-up ticket.
5. Re-check the strictness ledger. For each non-strict row, list its unmet tighten-triggers. If a trigger has changed, propose tightening.
6. Batch the "ask the user" findings into one `AskQuestion`.
7. Fix the "fix now" findings by looping back to stage 3, which then goes through stage 4. Repeat this review on the new diff until a pass produces no fix-now findings.

## Gate

- [ ] Every checklist line was checked against the final diff.
- [ ] Every finding is recorded and resolved as fixed, answered by the user, or logged.
- [ ] Stage 4's gate still holds after the last loop.
