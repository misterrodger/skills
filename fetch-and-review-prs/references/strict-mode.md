# Nudges on the GitHub PR

Every run posts nudge labels on the GitHub PR. Do not leave them as a draft for later approval. Do not put them on the Jira ticket.

## Labels

Use only these, comma-separated, in this order:

- `red pipeline` — CI red
- `pending pipeline` — CI pending
- `conflicts` — merge conflicts
- `unresolved comments` — unresolved review threads
- `changes requested`
- `stale` — open ≥ `staleOpenDays` or quiet ≥ `staleUpdateDays`

A missing approval is not a label. When a triage PR is ready, no pod senior has approved it, and `principal.login` has not approved it, `senior-tag.md` mentions those seniors on the PR.

`scripts/pr-readiness.sh` puts the matching labels on `nudges`. Drop nudges for drafts and for `files.i18nOnly` PRs. `check resolved` is not a GitHub label. It stays in the local summary when `reviewThreads.prematureResolve` is true.

Posted body is the labels only, for example `red pipeline, unresolved comments`.

## Where they appear

Lead the chat summary with **Nudges**. Write the same table in the day's `readiness.md` and `INDEX.md`: author, PR, labels, and whether the comment was posted or skipped by cooldown.

## Posting

Post on every run, including a normal `/fetch-and-review-prs` pass. `strict-nudge`, “make it strict”, and “strict mode” mean the same post. They are not a separate approval step.

```bash
gh pr comment NUMBER --repo OWNER/REPO --body "red pipeline, unresolved comments"
```

Skip a PR whose nudge fingerprint `(labels)` is unchanged and `lastStrictNudgeAt` is within `strictNudgeCooldownHours`. After a post, set `lastStrictNudgeAt` and store the label fingerprint.

Template: `/Users/jrodger/Github/pr-reviews/templates/strict-nudge-comment.md`

Senior mentions are a different GitHub comment on the same PR. Follow `senior-tag.md`.
