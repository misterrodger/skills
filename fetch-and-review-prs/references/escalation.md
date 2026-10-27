# Escalation without a full diff

`scripts/pr-readiness.sh` records the cheap signals. Use them before reading a patch.

## Ignore flagged/approved PRs

A PR with `flaggedOrApproved` true (GitHub label `flagged` or `approved`) is never skimmed, spot-checked, or escalated; `escalation.recommend`/`reasons` are already zeroed by `scripts/pr-readiness.sh`. Record it in the day's Flagged/Approved section instead. See `flagged-approved.md`.

## Ignore i18n volume

`files.i18nOnly` means every changed file is a translation or locale resource. Leave that PR out of full review, spot-check, escalation, and the nudge list, including when a senior wrote it. Record it in the day's deferred-i18n section. See `deferred-senior-triage.md`.

A mixed PR stays in scope. Size and hot-path checks already ignore locale files (`files.nonI18nCount`, `files.nonI18nLines`, `files.hotPaths`).

An i18n-only PR from a triage author that is ready to merge still gets a proposed senior mention under `senior-tag.md`, then stops.

## Script reasons

`escalation.recommend` is true when `escalation.reasons` contains any of:

- `bugbot-high` — Bugbot review text rates the risk high. This is one input, not the decision.
- `bugbot-medium` — included only when another script reason is also present. Medium alone does not escalate.
- `hot-path` — a non-i18n file matches API or schema, auth or permissions, migrations, feature flags, or generated clients.
- `large-diff` — non-i18n file count ≥ `largeNonI18nFiles` (25) or non-i18n changed lines ≥ `largeNonI18nLines` (800).
- `premature-resolve` — a non-outdated thread was resolved by the PR author and the reviewer has no later reply.

Bugbot `low`, `unknown`, or `none` never escalates by itself.

## Reasons added during the run

Add these on top of the script reasons:

- `multi-repo` — the same Jira key appears on open PRs in more than one repository in this run.
- `churn` — compared with the previous `state/prs/*.json`, CI status or review decision flipped, or the head SHA changed while CI stayed red.

If either is present, treat the PR as recommended for a skim even when `escalation.recommend` was false.

## Skim, then decide

When a triage PR is recommended, skim only:

- `files.nonI18nPaths` and `files.hotPaths`
- `reviewThreads.resolvedExcerpts`, especially `premature: true`
- `commitMessages`
- `bugbot.excerpt`

Do not run `gh pr diff` during the skim. Add a proposed full review when the skim still shows a material contract, auth, migration, or unresolved-looking comment. Otherwise mark the PR `watch` and leave the previous review in place.

Drafts are not skimmed or fully reviewed unless John asks.

## Spot-check

For each triage author, at most `maxSpotChecksPerAuthorPerRun` (1) quiet PR per run:

- not draft
- not `files.i18nOnly`
- no escalation reason and not `watch` from a skim this run
- no `lastDeepReviewAt` or `lastSpotCheckAt` within `spotCheckIntervalDays` (7)

Prefer the PR closest to merge: CI green, then mergeable, then oldest. Propose a full review labeled spot-check; do not read the diff yet. If John explicitly selects it, rerun readiness, perform the full review, label the cluster note as a spot-check, and then set `lastSpotCheckAt` and `lastSpotCheckSha`.

Triage authors are Marcos Aguilera, Chad Lott, Vladimir Koshcheyev, Juan David Varela, Francisco de Freitas, and Edwar Figueroa.
