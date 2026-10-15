---
name: fetch-and-review-prs
description: Fetch open PRs for John's pods, triage CI, resolved and unresolved comments, and file signals, and deep-review seniors plus escalated or spot-checked PRs. Post nudge labels on the GitHub PR. Mention pod seniors on the GitHub PR when a triage PR is ready without a senior or principal approval. i18n-only PRs are deferred. Use for a daily PR pass, named authors, or strict-nudge.
---

# Fetch and Review PRs

Orchestrates team PR triage and deep review into `/Users/jrodger/Github/pr-reviews/`.

## When to Use

- Daily / multi-daily team PR pass (`/fetch-and-review-prs`)
- “Review PRs from …” (override authors)
- Stale PR close triage
- `strict-nudge` is the same GitHub post as a normal run; it is not a separate approval step

## Load first

1. [`references/team.json`](references/team.json)
2. [`references/context-staleness.md`](references/context-staleness.md)
3. [`references/readiness.md`](references/readiness.md)
4. [`references/escalation.md`](references/escalation.md)
5. [`references/senior-tag.md`](references/senior-tag.md)
6. [`references/deferred-senior-triage.md`](references/deferred-senior-triage.md)
7. [`references/strict-mode.md`](references/strict-mode.md)
8. [`references/review-output-template.md`](references/review-output-template.md)

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
- `reviewDepth` `full`: readiness, plus a full review when the latest commit or the Jira acceptance criteria changed, or the PR was never reviewed.
- `reviewDepth` `triage`: readiness, nudges, and cheap signals. Full review only when a skim confirms an escalation, a spot-check is due, or John asks.
- Summarize in `summaryOrder`. Within a pod, seniors first.
- Full by default: Pod 19 seniors, Isis Salamanca, and Jonathan Harrison.
- Triage by default: Marcos Aguilera, Chad Lott, Vladimir Koshcheyev, Juan David Varela, Francisco de Freitas, and Edwar Figueroa.

A full review reads the branch diff. Skip that read when `headSha` still equals `lastDeepReviewSha` and the Jira acceptance criteria are unchanged. Refresh readiness only and keep the previous cluster note.

## Workflow (every run)

### 1. Resolve mode

- Every run: write local files, post nudge labels on the GitHub PR, and mention pod seniors on that PR when `senior-tag.md` says so. Do not comment on Jira for either action.
- `strict-nudge` / “make it strict” / “strict mode” posts the same GitHub comments. Follow `strict-mode.md`.

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

Bucket with `readiness.md`. i18n-only PRs go to the deferred-i18n section, not the review buckets.

### 5. Nudges

Copy `nudges` into the chat summary and the day's **Nudges** section. Drop drafts and i18n-only PRs. Post each remaining nudge on that GitHub PR. Follow `strict-mode.md` for the body and the cooldown.

### 6. Senior tags

Follow `senior-tag.md` for triage authors. Mention the pod seniors on the GitHub PR when the gate matches and the cooldown allows. Skip the mention when `principal.login` is already in `approvals.logins`. Do not comment on Jira. Report posts and cooldown skips in **Senior tagged**.

### 7. Cluster by Jira key

Extract `[A-Z][A-Z0-9]+-[0-9]+` from title, body, and branch. Same key → one cluster file. No key → `no-ticket__<repo>__pr-<n>.md`. A key on PRs in more than one repository adds the `multi-repo` reason.

### 8. Escalate, skim, spot-check

Follow `escalation.md`.

- i18n-only: deferred section only, plus a senior tag when that gate matches.
- Triage PR with an escalation reason: skim paths, excerpts, commit messages, and Bugbot text. Full review only when the skim is still material. Otherwise `watch`.
- Quiet triage PR due for a spot-check: one full review per author, labeled spot-check.
- `check resolved` stays in the local summary whenever `prematureResolve` is true.

### 9. Context and full review

For a full review that is new or whose `headSha` or Jira acceptance criteria changed:

- Jira: Atlassian `getJiraIssue`, using `context-staleness.md`.
- Confluence and `/Users/jrodger/Github/planning` when the ticket context is thin.
- Prefer a local Command_Alkon checkout: `git fetch` then `git diff <base>...<head>` (`develop` unless the PR base differs). Otherwise `gh pr diff` and note the limited context.
- Read `resolvedExcerpts` before calling a resolved comment handled.
- Apply, in order: `command-alkon-best-practices`, `dev-coding-practices`, `typescript-type-safety`, `test-code-quality`, and `pr-review` (including its security review unless John skips it).
- Also check conflicts, size, secrets, OpenAPI drift, feature flags, migrations, logging, and draft status. Do not treat locale file volume as principal scope.
- Write the cluster note. Set `lastDeepReviewSha` and `lastDeepReviewAt`. On a spot-check, also set `lastSpotCheckAt` and `lastSpotCheckSha`, and say the note is a spot-check.

When nothing new changed, refresh the Readiness section of the existing cluster note.

### 10. Finish

Update INDEX links. Lead the chat summary with nudges posted on GitHub, then senior mentions posted on GitHub, deferred i18n, escalations and spot-checks, then ready / blocked / very stale counts and the paths written.

## Initial / triage-only runs

If John asks for a first pass or to close stale PRs, prioritize readiness, nudges, senior tags, and staleness. Deep-review only non-stale full-depth PRs, confirmed escalations, and due spot-checks. Never auto-close PRs.

## Outputs

- Chat summary, nudges first
- `pr-reviews/YYYY-MM-DD/INDEX.md`
- `pr-reviews/YYYY-MM-DD/readiness.md`
- Cluster markdown for full reviews
- `pr-reviews/state/prs/*.json`
- Optional context under `pr-reviews/context/`
- A GitHub nudge comment when `strict-mode.md` matches
- A GitHub senior mention when `senior-tag.md` matches
