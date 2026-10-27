# Fetch and Review PRs

Team PR triage + deep review into `~/Github/pr-reviews/`.

## Invoke

- `/fetch-and-review-prs` — all default authors, at their configured depth
- “Review PRs from \<name\>” — additive, or only those people if the request says only/just
- “Fully review \<name/pod/PR\>” — deep-review even when the author is triage
- “Post these nudges” / “post these senior mentions” — execute only the selected proposed comments
- `strict-nudge` proposes nudge comments unless the request explicitly says to post

## Default review groups

| Group | Full-depth proposals | Default triage |
|-------|----------------------|----------------|
| Pod 19 — Sales and Quoting, and Pricing (primary) | Fabian Martinez, Sebastian Vasquez, Juan Pablo Betancourt, Andres Uribe | Marcos Aguilera, Chad Lott, Vladimir Koshcheyev |
| Pod 15 — Scale Ticketing (secondary) | Isis Salamanca; Sulakshana Sawsarikar (authored PRs scoped to bulk-materials-owned repos) | Juan David Varela, Francisco de Freitas, Edwar Figueroa |
| Peer | Jonathan Harrison | — |

A default pass proposes full reviews when due; it does not read diffs. An explicitly selected full review is repeated when the latest commit or the Jira acceptance criteria change. An unchanged diff is not re-read.

Triage PRs get readiness, proposed short nudge labels, and cheap file, comment, and Bugbot signals. A full review is proposed when a skim confirms the signal or a 7-day spot-check is due, and runs only when John selects it. i18n-only PRs are listed and left for a later Senior/Lead triage skill. A merge conflict confined to documentation files (a `docs/` path, `.md`/`.mdx`, README/CHANGELOG/CONTRIBUTING/LICENSE — e.g. a feature map) does not get a `conflicts` nudge; a developer can resolve that trivially and it shouldn't block a review.

A triage PR that is green, has no approval from a senior on its pod, and has no approval from `principal.login` gets a proposed GitHub comment mentioning those seniors. Skip that proposal when the principal has already approved. Nudge labels and senior mentions are posted only after explicit approval, never on the Jira ticket.

A PR carrying the GitHub label `flagged` or `approved` (either or both) is skipped entirely — no nudge, no senior mention, no skim/escalation/spot-check, no full review — and is only listed in a dedicated Flagged/Approved section.

Sulakshana's authored PRs are listed only from `cds-bulk-materials-service`, `cds-bulk-materials-exp`, `cds-bm-yard`, and `connex-asphalt-node-v4`. Her approvals satisfy the Pod 15 senior gate in every repository.

## What you get

Output sections are reported with **Proposed full reviews first**, then proposed nudges and senior mentions. A PR already listed under Proposed full reviews is not repeated under Escalations.

| Artifact | Updated |
|----------|---------|
| `pr-reviews/YYYY-MM-DD/INDEX.md` | Every run |
| `pr-reviews/YYYY-MM-DD/readiness.md` | Every run |
| Cluster `*.md` | When a selected full review runs |
| `state/prs/*.json` | Every run |
| Proposed full reviews | When full-depth, escalation, or spot-check criteria match — reported first |
| Proposed nudge list | Every run, when a PR has nudge labels |
| Proposed senior mentions | When a ready triage PR has no senior or principal approval |
| Flagged/Approved list | When a PR carries the GitHub label `flagged` or `approved`; informational only |
| GitHub comments / deep reviews | Only after explicit selection |

## Related skills

- `/command-alkon-best-practices`
- `pr-review`, `dev-coding-practices`, `typescript-type-safety`, `test-code-quality`
