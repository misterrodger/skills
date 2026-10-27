# Proposed senior tag and approved posting

When a triage author's PR is ready for a senior, no senior on that pod has approved it, and `principal.login` from `team.json` is not in `approvals.logins`, propose a GitHub comment and do not review the PR yourself. Do not post until John explicitly approves that mention. Do not comment on the Jira ticket.

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

Pod 19 seniors are Fabian Martinez (`fmartinez_cmd`), Sebastian Vasquez (`svasquez_cmd`), Juan Pablo Betancourt (`jpbetancourt_cmd`), and Andres Uribe (`auribe_cmd`). Pod 15 seniors are Isis Salamanca (`isalamanca_cmd`) and Sulakshana Sawsarikar (`sawsarikar_cmd`). Sulakshana's approval satisfies the Pod 15 senior gate on any PR, even though `repoScope` limits which of her authored PRs appear in this workflow. Use each senior's `login` from `team.json`.

This still applies when `files.i18nOnly` is true. Propose the mention, then stop. Do not add a label nudge or propose a full review for that PR.

If the same PR also has a principal signal from `escalation.md`, propose the mention and still surface that signal.

Label nudges are a separate GitHub comment with separate approval. Follow `strict-mode.md`.

## Comment

```bash
gh pr comment NUMBER --repo OWNER/REPO --body "please review @fmartinez_cmd, @svasquez_cmd, @jpbetancourt_cmd, or @auribe_cmd"
```

One line: `please review `, then `@login` for each pod senior, separated by `, `, with ` or ` before the last mention.

Pod 19: `please review @fmartinez_cmd, @svasquez_cmd, @jpbetancourt_cmd, or @auribe_cmd`

Pod 15: `please review @isalamanca_cmd or @sawsarikar_cmd`

## Approved posting and cooldown

Before posting an explicitly selected mention, rerun readiness and recheck every gate. Skip it if the PR is closed or any gate no longer matches.

Fingerprint is the sorted senior logins. If `lastSeniorTagAt` is within `strictNudgeCooldownHours` and `seniorTagFingerprint` is unchanged, do not comment again. Store both fields on the PR state only after a successful post; a proposal does not update either field.
