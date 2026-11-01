# Slice note template

Copy this file to `~/Github/planning/zod-fullstack-type-safety/slices/<yyyy-mm-dd>-<domain>-<resource>.md` at stage 1, and keep it updated. Keep entries short; this is a working record, not a report.

```markdown
# <domain> / <resource> slice

Started <date>. Jira: <key or none>.

## Scope (confirmed <date>)

| Repo | Files / handlers | Branch |
| --- | --- | --- |

Out of scope, noted for later:

## Behaviour (stage 0)

| Behaviour | Seam | Test | Decision |
| --- | --- | --- | --- |
|  |  |  | preserve / correct on purpose / later ticket |

## Strictness ledger

| Object | Schema | Mode | Source evidence | Approved by user | Unmet tighten-triggers | Last reviewed |
| --- | --- | --- | --- | --- | --- | --- |
|  |  | strict / non-strict (why) |  | n/a for strict |  |  |

## Constants candidates

| Constant | Used in | Recommended home | Decision |
| --- | --- | --- | --- |

## Transform candidates

| App-side transform | Where | Proposed contract transform | Decision |
| --- | --- | --- | --- |

## DAO signatures made specific

| DAO function | Before | After |
| --- | --- | --- |

## Guards added for the checker

| File | Guard | Why it couldn't be fixed upstream |
| --- | --- | --- |

## Findings log

| Stage | Finding | Outcome (fixed / asked / logged) |
| --- | --- | --- |

## Bugs the typing found

## Still legacy next door

## OpenAPI (stage 7)

Baseline file: <path>. Drift test: <path>. Merge function: <path or n/a>.
```

## Tighten-triggers

A non-strict object can be made strict once all of these hold. Proposing it is a separate commit, behind the stage 0 tests, after the user agrees:

1. The contract models every field the source schema defines, plus fields other writers persist.
2. A sample of stored records from dev parses with the strict schema and nothing is dropped or rejected.
3. Every writer goes through the contract, or is known and listed.
4. Each field made required or non-nullable is backed by the stored-data sample, not only by the old schema.

When a later slice touches an object with a ledger row, re-check its unmet triggers. Ask the user about tightening only when a trigger has changed.
