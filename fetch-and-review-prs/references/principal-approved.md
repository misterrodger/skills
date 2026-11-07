# Approved by you: out of the action queues

A pull request John has already approved, and whose approval is still current, is not work for this pass. Listing it again as a review, nudge, mention, or watch item is noise.

## Gate

`scripts/pr-readiness.sh` sets `principalApproved` to true when `approvals.logins` contains `principal.login` from `team.json` (`jdrodger_cmd`).

That list is built from the latest review per user whose state is `APPROVED`. A dismissed, commented, or changes-requested review does not count. After a new commit dismisses John's approval, `principalApproved` becomes false and the pull request returns to the normal queues.

`flaggedOrApproved` still wins. A pull request that is both flagged and approved by John is listed only under Flagged / Approved.

## What to skip

For a pull request with `principalApproved` true:

- No nudge, including stale, conflicts, red pipeline, and unresolved comments.
- No senior mention.
- No skim, spot-check, or escalation.
- No proposed full review, including for a full-depth author.
- Do not cluster it into a Jira-key review file.
- Leave it out of Ready, Blocked, Stale watch, and Very stale.

The script already zeroes `nudges` and `escalation.recommend` / `escalation.reasons` when the gate matches.

## What to record

List it once in the day's **Approved by you** section: author, `repo #number` link, title, and Jira key when present. One line is enough. This section is informational. It is not a queue.

Do not propose an action for it unless John explicitly asks to review that pull request anyway.
