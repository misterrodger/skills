# Proposed nudges and approved posting

Every triage run reports proposed nudge labels but does not post them. Post only when John explicitly approves selected nudges. Do not put them on the Jira ticket.

## Labels

Use only these, comma-separated, in this order:

- `red pipeline` — CI red
- `pending pipeline` — CI pending
- `conflicts` — merge conflicts
- `unresolved comments` — unresolved review threads
- `changes requested`
- `stale` — open ≥ `staleOpenDays` or quiet ≥ `staleUpdateDays`

A missing approval is not a label. When a triage PR is ready, no pod senior has approved it, and `principal.login` has not approved it, `senior-tag.md` proposes a separate senior mention.

`scripts/pr-readiness.sh` puts the matching labels on `nudges`. Drop nudges for drafts and for `files.i18nOnly` PRs. The script also skips `conflicts` when `files.docsOnly` is true — every changed file is documentation (a `docs/` path, `.md`/`.mdx`, or a README/CHANGELOG/CONTRIBUTING/LICENSE file, e.g. a feature map) — because a docs-only conflict is trivial for the author to resolve and should not block or nudge. A mixed PR (docs plus code) still nudges normally. Drop all nudges for a PR whose `flaggedOrApproved` is true; see `flagged-approved.md`. `check resolved` is not a GitHub label. It stays in the local summary when `reviewThreads.prematureResolve` is true.

Posted body is the labels only, for example `red pipeline, unresolved comments`.

## Proposal output

Lead the chat summary with **Proposed nudges**. Write the same table in the day's `readiness.md` and `INDEX.md`: author, PR, labels, and status (`awaiting approval`, `posted`, or the revalidation/cooldown skip reason).

## Approved posting

`strict-nudge`, “make it strict”, and “strict mode” request proposals unless the same request explicitly says to post. A follow-up such as “post all proposed nudges” or “post the nudge on OWNER/REPO#123” authorizes only that scope.

Before posting, rerun `scripts/pr-readiness.sh` for each selected PR. Use the current labels, and skip the action if it is now a draft, i18n-only, closed, or has no nudge labels.

```bash
gh pr comment NUMBER --repo OWNER/REPO --body "red pipeline, unresolved comments"
```

Skip a PR whose current nudge fingerprint `(labels)` is unchanged and `lastStrictNudgeAt` is within `strictNudgeCooldownHours`. Update `lastStrictNudgeAt` and the label fingerprint only after a successful post; a proposal does not update either field.

Template: `/Users/jrodger/Github/pr-reviews/templates/strict-nudge-comment.md`

Senior mentions require separate approval even when the same PR has a proposed nudge. Follow `senior-tag.md`.
