---
name: fetch-and-review-prs
description: Fetch open PRs for John's pods, triage CI, comments, and file signals, then propose nudge comments, senior mentions, and full reviews without posting or reviewing by default. Execute only the actions John explicitly selects in a follow-up request. i18n-only PRs are deferred. Use for a daily PR pass, named authors, review requests, or approved nudge and senior-tag actions.
---

# Fetch and Review PRs

Orchestrates approval-gated team PR triage and review into `/Users/jrodger/Github/pr-reviews/`.

## When to Use

- Daily / multi-daily team PR pass (`/fetch-and-review-prs`)
- “Review PRs from …” or “review PR …” (explicit review authorization)
- “Post these nudges” or “tag seniors on …” (explicit GitHub comment authorization)
- Stale PR close triage
- `strict-nudge` only proposes comments unless the request explicitly says to post them

## Load first

1. [`references/team.json`](references/team.json)
2. [`references/context-staleness.md`](references/context-staleness.md)
3. [`references/readiness.md`](references/readiness.md)
4. [`references/escalation.md`](references/escalation.md)
5. [`references/senior-tag.md`](references/senior-tag.md)
6. [`references/flagged-approved.md`](references/flagged-approved.md)
7. [`references/deferred-senior-triage.md`](references/deferred-senior-triage.md)
8. [`references/strict-mode.md`](references/strict-mode.md)
9. [`references/review-output-template.md`](references/review-output-template.md)

## Paths

| Role | Path |
|------|------|
| Reviews root | `/Users/jrodger/Github/pr-reviews` |
| Planning | `/Users/jrodger/Github/planning` |
| Repos | `/Users/jrodger/Github/Command_Alkon` (or `$COMMAND_ALKON_HOME`) |
| List script | `scripts/list-open-prs.sh` |
| Readiness script | `scripts/pr-readiness.sh` |

## Author resolution

- Default: all `defaultAuthors` in `team.json`.
- Extra names/logins: **additive** unless the user says only/just those people.
- Match aliases case-insensitively to `login`.
- After listing PRs, restrict an author's rows to `repoScope` when that field is present. The scope limits authored PRs only; the author's approvals still count wherever the pod-senior gate applies.
- `reviewDepth` `full`: readiness plus a proposed full review when the latest commit changed or the PR was never reviewed. Recheck Jira acceptance criteria before an approved review.
- `reviewDepth` `triage`: readiness, proposed nudges, and cheap signals. Propose a full review when a skim confirms an escalation or a spot-check is due.
- Summarize in `summaryOrder`. Within a pod, seniors first.
- Full-depth proposal group: Pod 19 seniors, Pod 15 seniors Isis Salamanca and Sulakshana Sawsarikar, and Jonathan Harrison.
- Triage by default: Marcos Aguilera, Chad Lott, Vladimir Koshcheyev, Juan David Varela, Francisco de Freitas, and Edwar Figueroa.

A full review reads the branch diff only after John explicitly requests that review. Skip that read when `headSha` still equals `lastDeepReviewSha` and the Jira acceptance criteria are unchanged. Refresh readiness only and keep the previous cluster note.

## Workflow (every run)

### 1. Resolve mode

- **Triage/proposal mode is the default.** Write local files and report proposed nudges, senior mentions, and full reviews. Do not post GitHub comments, fetch full diffs, or run the review skill stack.
- **Execution mode requires explicit action and scope.** Requests such as “post these nudges,” “post the proposed senior mentions,” or “review PR 123” authorize only the selected actions. Do not infer approval for the other queues.
- Before an approved action, rerun readiness for each selected PR. Drop or update actions whose current state no longer matches. Follow `strict-mode.md`, `senior-tag.md`, and the review freshness checks.
- Never comment on Jira as part of a nudge or senior mention.

### 2. List open PRs

```bash
bash ~/.claude/skills/fetch-and-review-prs/scripts/list-open-prs.sh LOGIN1 LOGIN2 ...
```

### 3. Day folder + run log

- Ensure `pr-reviews/YYYY-MM-DD/`.
- Append a row to `INDEX.md`. Start from `/Users/jrodger/Github/pr-reviews/templates/day-index.md` when the file is new.
- Write/refresh `readiness.md`.

### 4. Readiness per PR

```bash
bash ~/.claude/skills/fetch-and-review-prs/scripts/pr-readiness.sh OWNER/REPO NUMBER
```

Merge into `state/prs/<owner>__<repo>__<n>.json`. Preserve `lastDeepReviewAt`, `lastDeepReviewSha`, `lastSpotCheckAt`, `lastSpotCheckSha`, `lastStrictNudgeAt`, `lastSeniorTagAt`, and `seniorTagFingerprint`.

Bucket with `readiness.md`. i18n-only PRs go to the deferred-i18n section, not the review buckets. PRs with `flaggedOrApproved` true go to the Flagged/Approved section, not any review bucket.

### 5. Flagged / approved PRs

Follow `flagged-approved.md`. Any PR with `flaggedOrApproved` true (GitHub label `flagged` or `approved`) is pulled out here, before nudges, senior tags, clustering, or escalation run. List it once in the day's **Flagged / Approved** section (author, PR, Jira key if present, matched label(s)) and skip it entirely in steps 6–10.

### 6. Nudges

Copy `nudges` into the chat summary and the day's **Proposed nudges** section. Drop drafts, i18n-only PRs, and flagged/approved PRs (their `nudges` array is already empty). Do not post them in triage/proposal mode. In execution mode, post only the explicitly selected, revalidated nudges. Follow `strict-mode.md` for the body, cooldown, and state update.

### 7. Senior tags

Follow `senior-tag.md` for triage authors. Add matches to **Proposed senior mentions**; do not post them in triage/proposal mode. In execution mode, post only explicitly selected, revalidated mentions. Skip the mention when `principal.login` is already in `approvals.logins` or the PR is flagged/approved.

### 8. Cluster by Jira key

Extract `[A-Z][A-Z0-9]+-[0-9]+` from title, body, and branch. Same key → one cluster file. No key → `no-ticket__<repo>__pr-<n>.md`. A key on PRs in more than one repository adds the `multi-repo` reason. Flagged/approved PRs are not clustered.

### 9. Escalate, skim, spot-check

Follow `escalation.md`.

- Flagged/approved: out of scope entirely, see step 5. Not skimmed, spot-checked, or escalated.
- i18n-only: deferred section only, plus a proposed senior mention when that gate matches.
- Triage PR with an escalation reason: skim paths, excerpts, commit messages, and Bugbot text. Propose a full review when the skim is still material. Otherwise `watch`.
- Quiet triage PR due for a spot-check: propose at most one full review per author, labeled spot-check.
- `check resolved` stays in the local summary whenever `prematureResolve` is true.

### 10. Proposed reviews

- Add full-depth candidates, confirmed escalations, and due spot-checks to **Proposed full reviews** with the reason for each recommendation. This section is reported first, ahead of nudges and senior mentions.
- Do not fetch the branch diff or run review skills in triage/proposal mode.
- If a candidate has an unchanged `headSha`, defer the Jira acceptance-criteria freshness check until John selects it.
- Never add a flagged/approved PR here.

### 11. Execute selected full reviews

For each explicitly selected review, refresh readiness and Jira context first. Continue only when the review is new or `headSha` or Jira acceptance criteria changed:

- Jira: Atlassian `getJiraIssue`, using `context-staleness.md`.
- Confluence and `/Users/jrodger/Github/planning` when the ticket context is thin.
- Prefer a local Command_Alkon checkout: `git fetch` then `git diff <base>...<head>` (`develop` unless the PR base differs). Otherwise `gh pr diff` and note the limited context.
- Read `resolvedExcerpts` before calling a resolved comment handled.
- Apply, in order: `command-alkon-best-practices`, `dev-coding-practices`, `typescript-type-safety`, `test-code-quality`, and `pr-review` (including its security review unless John skips it).
- Also check conflicts, size, secrets, OpenAPI drift, feature flags, migrations, logging, and draft status. Do not treat locale file volume as principal scope.
- Write the cluster note. Set `lastDeepReviewSha` and `lastDeepReviewAt`. On a spot-check, also set `lastSpotCheckAt` and `lastSpotCheckSha`, and say the note is a spot-check.

When nothing new changed, refresh the Readiness section of the existing cluster note.

### 12. Finish

Update INDEX links. In proposal mode, lead with **proposed full reviews** first, then proposed nudges, then proposed senior mentions. In execution mode, lead with actions actually completed and list any selected actions skipped after revalidation. Then report flagged/approved, deferred i18n, escalations (omit any PR already listed under proposed full reviews — no duplicates), watch signals, ready / blocked / very stale counts, and paths written.

## Initial / triage-only runs

If John asks for a first pass or to close stale PRs, prioritize readiness, proposed nudges, proposed senior tags, and staleness. Propose non-stale full-depth PRs, confirmed escalations, and due spot-checks for review. Never auto-close PRs.

## Outputs

- Chat summary, proposed actions first
- `pr-reviews/YYYY-MM-DD/INDEX.md`
- `pr-reviews/YYYY-MM-DD/readiness.md`
- Cluster markdown only for explicitly selected full reviews
- `pr-reviews/state/prs/*.json`
- Optional context under `pr-reviews/context/`
- Proposed full-review list, reported first; review only when explicitly selected
- Proposed GitHub nudge comments; post only when explicitly selected
- Proposed GitHub senior mentions; post only when explicitly selected
- Flagged/Approved list (GitHub label `flagged` or `approved`); informational only, never reviewed
