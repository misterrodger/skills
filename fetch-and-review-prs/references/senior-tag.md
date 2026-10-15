# Senior tag on the GitHub PR

When a triage author's PR is ready for a senior, no senior on that pod has approved it, and `principal.login` from `team.json` is not in `approvals.logins`, comment on that GitHub PR and do not review the PR yourself. Do not comment on the Jira ticket.

## Gate

All of:

- author `reviewDepth` is `triage`
- not draft
- CI `green`
- unresolved threads = 0
- `mergeable` is `MERGEABLE`
- `changesRequested` is 0
- no `approvals.logins` entry is a senior `login` from the author's pod
- no `approvals.logins` entry is `principal.login` from `team.json`

An approval from `principal.login` suppresses the senior mention the same way a pod-senior approval does. Do not ask the pod seniors to review a PR the principal has already approved.

A Jira key is not required. The comment is on the PR.

Pod 19 seniors are Fabian Martinez (`fmartinez_cmd`), Sebastian Vasquez (`svasquez_cmd`), Juan Pablo Betancourt (`jpbetancourt_cmd`), and Andres Uribe (`auribe_cmd`). Pod 15's senior is Isis Salamanca (`isalamanca_cmd`). Use each senior's `login` from `team.json`.

This still applies when `files.i18nOnly` is true. Post the mention, then stop. Do not add the label nudge and do not review that PR.

If the same PR also has a principal signal from `escalation.md`, post the mention and still surface that signal.

Label nudges are a separate GitHub comment. Follow `strict-mode.md`. Post both when both rules match.

## Comment

```bash
gh pr comment NUMBER --repo OWNER/REPO --body "please review @fmartinez_cmd, @svasquez_cmd, @jpbetancourt_cmd, or @auribe_cmd"
```

One line: `please review `, then `@login` for each pod senior, separated by `, `, with ` or ` before the last mention.

Pod 19: `please review @fmartinez_cmd, @svasquez_cmd, @jpbetancourt_cmd, or @auribe_cmd`

Pod 15: `please review @isalamanca_cmd`

## Cooldown

Fingerprint is the sorted senior logins. If `lastSeniorTagAt` is within `strictNudgeCooldownHours` and `seniorTagFingerprint` is unchanged, do not comment again. After a post, store both fields on the PR state.
