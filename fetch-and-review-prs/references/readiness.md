# PR readiness interpretation

Collected by `scripts/pr-readiness.sh` (and/or equivalent `gh` calls).

## CI

| Status | Meaning |
|--------|---------|
| `green` | All reported checks success (or neutral/skipped only) |
| `red` | Any failure / cancelled as failure |
| `pending` | Any pending/queued/in_progress |
| `unknown` | Checks API empty or error |

Failing check **names** go in `ciDetail`.

## Comment threads

GraphQL review threads supply `isResolved`, `isOutdated`, `resolvedBy`, and comment excerpts.

Classify authors:

- **Bugbot** — login/name contains `bugbot`, `cursor`, or known bot apps
- **human** — everyone else

Count unresolved and resolved threads. Resolved is not clean. `prematureResolve` is true when a non-outdated thread was resolved by the PR author and the reviewer has no later reply. Full reviews must read `resolvedExcerpts` before treating that comment as handled. Surface those as the local signal `check resolved`. Do not put that phrase in a GitHub nudge.

Bugbot's risk words are stored on `bugbot`. They are one escalation input. See `escalation.md`.

## Approvals

Count `APPROVED` reviews from users **≠ PR author**. `CHANGES_REQUESTED` blocks “ready” even if another approval exists.

Org standard (CA §13) may require **2** approvals + CODEOWNER. Note in INDEX when only one approval exists against that bar. GitHub nudge comments are proposed using the short labels in `strict-mode.md`. Senior mentions are a separate proposed GitHub comment in `senior-tag.md`. Neither is posted without explicit approval.

## Ready for your review (INDEX bucket)

All of:

- not draft (unless user asked to review drafts)
- not i18n-only (`files.i18nOnly`)
- CI green
- unresolved threads = 0
- ≥1 non-author approval
- not very stale

Resolved threads can still be present. List `check resolved` beside the row when `prematureResolve` is true. A triage PR that is green and unblocked is not this bucket when no senior on its pod has approved it. If `principal.login` is also absent from `approvals.logins`, add the comment to **Proposed senior mentions** under `senior-tag.md`. If `principal.login` is present, do not propose the mention.

## Blocked

Any of: CI red/pending, unresolved threads > 0, zero non-author approvals, merge conflicts.

## Flagged / approved (out of scope)

`flaggedOrApproved` true (GitHub label `flagged` or `approved`) takes a PR out of every other bucket and signal — no nudge, no senior mention, no escalation/skim/spot-check, no full review. List it once in the day's Flagged/Approved section instead. See `flagged-approved.md`.

## Very stale / stale watch

From `references/team.json` thresholds (`veryStaleOpenDays`, `staleOpenDays`, `staleUpdateDays`).
