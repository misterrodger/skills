# Flagged / approved: out of scope entirely

A PR carrying the GitHub label `flagged` or `approved` (case-insensitive, either or both) is not reviewed by this workflow at all. Someone has already marked it as handled or intentionally held, so John does not need a nudge, a senior mention, a skim, a spot-check, or a full review for it.

## Gate

`scripts/pr-readiness.sh` sets `flaggedOrApproved` to true when any entry in `labels` (case-insensitive) is `flagged` or `approved`. When true, the script already zeroes `nudges` and `escalation.recommend`/`escalation.reasons` for that PR, matching how `files.i18nOnly` is handled.

## What to skip

For a PR with `flaggedOrApproved` true:

- No nudge label, even if CI is red, there are merge conflicts, or it is stale.
- No senior mention (`senior-tag.md`).
- No skim, spot-check, or escalation reason (`escalation.md`).
- No proposed full review, even for a full-depth author or a pod senior.
- Do not cluster it into a Jira-key review file.

## What to record

List it once in the day's **Flagged / Approved** section: author, `repo #number` link, title, Jira key when present in title/body/branch, and which label(s) matched (`flagged`, `approved`, or both). This is the only place it appears in the output.

This is independent of `files.i18nOnly` and of draft status — a flagged/approved PR is skipped the same way whether or not it is also i18n-only or a draft.
